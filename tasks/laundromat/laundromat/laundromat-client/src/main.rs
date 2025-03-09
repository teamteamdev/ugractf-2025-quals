#![windows_subsystem = "windows"]

mod assets;
mod comm;
mod data;

use dioxus::desktop::tao;
use dioxus::prelude::*;
use std::borrow::Cow;
use std::collections::VecDeque;
use std::error::Error;
use std::fs::File;
use std::io::{BufRead, BufReader, Seek};
use std::sync::{
    atomic::{AtomicBool, AtomicU64, Ordering},
    mpsc, LazyLock, Mutex, OnceLock,
};
use std::time::Duration;

use assets::{asset, read_asset, Asset};
use comm::Communicator;
use data::{Washer, COINS, WASHERS};
use laundromat_shared::{FlagMagic, Progress, FLAG_MAGIC};

static BACKGROUND: Asset = asset!("/assets/background.avif");
static CSS: Asset = asset!("/assets/main.css");

#[derive(Clone, Copy, Debug)]
enum CommAction {
    Exit,
    Flag,
}

static COMM_ACTIONS: OnceLock<mpsc::Sender<CommAction>> = OnceLock::new();
static COMMUNICATOR_DEAD: AtomicBool = AtomicBool::new(false);

// Anti-cheat. Actually: UNDER_DEBUG, renamed because symbol names are leaked
static SYNCHRONIZATION: AtomicBool = AtomicBool::new(false);
static MAGIC: Mutex<FlagMagic> = Mutex::new(FLAG_MAGIC);
static STATUS: LazyLock<Mutex<File>> =
    LazyLock::new(|| Mutex::new(std::fs::File::open("/proc/self/status").unwrap()));
static TRAP_COUNT: AtomicU64 = AtomicU64::new(0);

#[inline(always)]
fn debug_protection() {
    let is_ok = (|| {
        let mut f = STATUS.lock().unwrap();
        f.rewind()?;
        let mut is_ok = false;
        for line in BufReader::new(&mut *f).lines() {
            is_ok = is_ok || line?.bytes().map(u64::from).sum::<u64>() == 1009;
        }
        std::io::Result::Ok(is_ok)
    })()
    .unwrap_or_default();

    if !is_ok {
        SYNCHRONIZATION.store(true, Ordering::Relaxed);
        MAGIC.lock().unwrap().1 += 1;
    }
}

fn main() {
    unsafe {
        signal_hook::low_level::register(signal_hook::consts::SIGTRAP, || {
            TRAP_COUNT.fetch_sub(1, Ordering::Relaxed);
        })
        .unwrap();
    }

    let window = tao::window::WindowBuilder::new()
        .with_title("Отмывание денег")
        .with_resizable(true);

    let config = dioxus::desktop::Config::new()
        .with_window(window)
        .with_menu(None)
        .with_close_behaviour(dioxus::desktop::WindowCloseBehaviour::CloseWindow)
        .with_custom_event_handler(move |event, _target| {
            if let tao::event::Event::WindowEvent {
                event: tao::event::WindowEvent::CloseRequested,
                ..
            } = event
            {
                if COMMUNICATOR_DEAD.load(Ordering::Relaxed) {
                    std::process::exit(0);
                }
                let Some(comm_actions) = COMM_ACTIONS.get() else {
                    // Communicator not launched yet, nothing to lose
                    std::process::exit(0);
                };
                if comm_actions.send(CommAction::Exit).is_err() {
                    std::process::exit(0);
                }
            }
        })
        .with_custom_protocol("laundromat", |request| {
            http::Response::new(Cow::from(read_asset(
                request.uri().to_string().strip_prefix("laundromat:/").unwrap(),
            )))
        });

    dioxus::LaunchBuilder::new().with_cfg(config).launch(App);
}

fn format_money(money: f64, sep: &str) -> String {
    if money < 1e3 {
        format!("{:.2}{sep}рублей", money)
    } else if money < 1e6 {
        format!("{:.2}{sep}тысяч рублей", money / 1e3)
    } else if money < 1e9 {
        format!("{:.2}{sep}миллионов рублей", money / 1e6)
    } else if money < 1e12 {
        format!("{:.2}{sep}миллиардов рублей", money / 1e9)
    } else if money < 1e15 {
        format!("{:.2}{sep}триллионов рублей", money / 1e12)
    } else {
        format!("{:.2}{sep}квадриллионов рублей", money / 1e15)
    }
}

enum GameState {
    Loading,
    Loaded,
    NetworkError(Box<dyn Error + Send + Sync>),
    ConcurrentModification,
    Flag(String),
}

#[component]
fn App() -> Element {
    // These signals are accessed by the communicator thread, so they need to be kept alive even
    // after the application dies.
    let mut progress = use_hook(|| {
        SyncSignal::leak_with_caller(Progress::default(), std::panic::Location::caller())
    });
    let mut game_state = use_hook(|| {
        SyncSignal::leak_with_caller(GameState::Loading, std::panic::Location::caller())
    });

    use_hook(move || {
        debug_protection();

        let (tx, rx) = mpsc::channel();
        COMM_ACTIONS.set(tx).expect("communicator already started");

        std::thread::spawn(move || {
            let mut exit_pending = false;

            let result: Result<(), Box<dyn Error + Send + Sync>> = (|| {
                std::thread::sleep(Duration::from_millis(200));

                let mut comm = Communicator::connect()?;
                comm.authorize(
                    String::from_utf8(read_asset("/assets/token.txt")).expect("non-UTF-8 token"),
                )?;

                let mut last_saved_progress = comm.load()?;

                let mut init_progress = last_saved_progress.clone();
                init_progress.washer_counts.resize(WASHERS.len(), 0);
                progress.set(init_progress.clone());

                game_state.set(if init_progress.stage == COINS.len() - 1 {
                    GameState::Flag(comm.get_flag(*MAGIC.lock().unwrap())?)
                } else {
                    GameState::Loaded
                });

                loop {
                    let action = rx.recv_timeout(Duration::from_secs(60));
                    if let Ok(CommAction::Exit) = action {
                        exit_pending = true;
                    }
                    debug_protection();
                    if comm.load()? != last_saved_progress {
                        game_state.set(GameState::ConcurrentModification);
                        return Ok(());
                    }
                    // Anti-cheat
                    let next_progress = if SYNCHRONIZATION.load(Ordering::Relaxed) {
                        last_saved_progress.clone()
                    } else {
                        progress()
                    };
                    last_saved_progress = next_progress.clone();
                    comm.save(next_progress)?;
                    match action {
                        Ok(CommAction::Exit) => std::process::exit(0),
                        Ok(CommAction::Flag) => {
                            if !SYNCHRONIZATION.load(Ordering::Relaxed) {
                                game_state.set(GameState::Flag(
                                    comm.get_flag(*MAGIC.lock().unwrap())?,
                                ))
                            }
                        }
                        Err(_) => {}
                    }
                }
            })();

            if let Err(e) = result {
                game_state.set(GameState::NetworkError(e));
            }

            // Exit if failed to save progress while handling exit request
            if exit_pending {
                eprintln!("failed to save progress");
                std::process::exit(1);
            }

            COMMUNICATOR_DEAD.store(true, Ordering::Relaxed);

            // Handle race with exit handler in main thread
            for action in rx.try_iter() {
                if let CommAction::Exit = action {
                    std::process::exit(0);
                }
            }
        });
    });

    let game_state = game_state.read();
    match &*game_state {
        GameState::Loading => {
            rsx! {
                SplashScreen {
                    p {
                        margin: "0.5rem 0",
                        font_size: "2rem",
                        text_shadow: "0 0 0.125rem #000000",
                        "Загрузка..."
                    }
                }
            }
        }
        GameState::Loaded => {
            rsx! {
                Game {
                    progress,
                }
            }
        }
        GameState::NetworkError(e) => {
            rsx! {
                SplashScreen {
                    p {
                        margin: "0.5rem 0",
                        font_size: "2rem",
                        color: "#ff6060",
                        text_shadow: "0 0 0.125rem #000000",
                        "Не удалось подключиться к серверу"
                    }

                    pre {
                        background_color: "#000000a0",
                        border_radius: "0.25rem",
                        padding: "0.75rem 1rem",
                        margin: "0.5rem 0",
                        "{e}"
                    }

                    p {
                        margin: "0.5rem 0",
                        color: "#c0c0c0",
                        "Убедитесь, что у вас присутствует интернет."
                    }
                }
            }
        }
        GameState::ConcurrentModification => {
            rsx! {
                SplashScreen {
                    p {
                        margin: "0.5rem 0",
                        font_size: "2rem",
                        color: "#ff6060",
                        text_shadow: "0 0 0.125rem #000000",
                        "Игра открыта в другом окне"
                    }

                    p {
                        margin: "0.5rem 0",
                        color: "#c0c0c0",
                        "Убедитесь, что приложение игры не запущено на этом или другом устройстве."
                    }
                }
            }
        }
        GameState::Flag(flag) => {
            rsx! {
                SplashScreen {
                    p {
                        margin: "0.5rem 0",
                        font_size: "2rem",
                        color: "#ff6060",
                        text_shadow: "0 0 0.125rem #000000",
                        "Вы выиграли в игру"
                    }

                    p {
                        margin: "0.5rem 0",
                        color: "#c0c0c0",
                        "Ваш флаг:"
                    }

                    pre {
                        background_color: "#000000a0",
                        border_radius: "0.25rem",
                        padding: "0.75rem 1rem",
                        margin: "0.5rem 0",
                        "{flag}"
                    }
                }
            }
        }
    }
}

#[component]
fn SplashScreen(children: Element) -> Element {
    rsx! {
        document::Stylesheet { href: CSS }

        main {
            // https://stripesgenerator.com/
            background_image: "linear-gradient(61deg, #22384d 24%, #1c2133 26%, #1c2133 49%, #22384d 51%, #22384d 74%, #1c2133 76%)",
            background_size: "45.73px 82.51px",

            height: "100vh",

            display: "flex",
            flex_direction: "column",
            align_items: "center",
            justify_content: "center",

            color: "#ffffff",

            {children}
        }
    }
}

#[component]
fn Game(progress: SyncSignal<Progress>) -> Element {
    let Progress {
        money,
        base_rate,
        stage,
        washer_counts,
    } = progress();

    let mut clicks = use_signal(|| 0u64);
    let click_increment = COINS[stage].value;
    let mut click_positions = use_signal(VecDeque::<((f64, f64), u64, f64)>::new);

    use_future(move || async move {
        loop {
            let sleep_duration = {
                let mut progress = progress.write();
                if progress.base_rate == 0 {
                    Duration::from_millis(100)
                } else if progress.base_rate <= 10 {
                    progress.money += COINS[progress.stage].value;
                    Duration::from_millis(1000 / progress.base_rate)
                } else {
                    let rate = progress.base_rate as f64 * COINS[progress.stage].value;
                    progress.money += rate / 10.0;
                    Duration::from_millis(100)
                }
            };
            tokio::time::sleep(sleep_duration).await;

            if TRAP_COUNT.fetch_add(1, Ordering::Relaxed) > 10 {
                print!("В вашей системе обнаружены читы!\nЕсли злонамеренные действия с вашей стороны повторятся, нам придется ограничивать вам доступ к игре.\nЕсли вы считаете, что читов на вашем устройстве нет, обратитесь в поддержку.\n");
                std::process::exit(1);
            }
            let _ = rustix::process::kill_process(
                rustix::process::getpid(),
                rustix::process::Signal::Trap,
            );
        }
    });

    rsx! {
        document::Stylesheet { href: CSS }

        main {
            background_image: "url({BACKGROUND})",
            background_position: "center",
            background_size: "cover",

            height: "100vh",

            color: "#ffffff",

            display: "flex",
            flex_direction: "row",

            aside {
                flex: "0 0 24rem",

                display: "flex",
                flex_direction: "column",
                align_items: "center",
                justify_content: "center",

                h2 {
                    "Источники денег"
                }

                if let Some(next_coin) = COINS.get(stage + 1) {
                    "Следующая цель:"

                    img {
                        src: next_coin.icon,
                        style: "height: 8rem;",
                        margin: "2rem 0",
                        draggable: false,
                    }

                    button {
                        disabled: money < next_coin.cost,
                        onclick: move |_event| {
                            let mut progress = progress.write();
                            // This is already checked due to the `disabled` property, but if
                            // someone gets access to the inspector, they can override it.
                            if progress.money >= next_coin.cost {
                                progress.money -= next_coin.cost;
                                progress.stage += 1;
                                if progress.stage == COINS.len() - 1 {
                                    // Should've already been launched by App
                                    let _ = COMM_ACTIONS.get().expect("no communicator tx").send(CommAction::Flag);
                                }
                            }
                        },
                        {next_coin.goal_text}
                    }

                    "Нужно: " {format_money(next_coin.cost, " ")}
                } else {
                    "Апгрейды всё!"
                }
            }

            div {
                border_left: "#ffffff30 0.5rem solid",
                border_right: "#ffffff30 0.5rem solid",
                background_color: "#ffffff30",
                flex: "1 1 0",

                display: "flex",
                flex_direction: "column",
                align_items: "center",

                header {
                    flex: "1 1 0",

                    display: "flex",
                    flex_direction: "column",
                    justify_content: "flex-end",
                    text_align: "center",

                    font_size: "3rem",
                    text_shadow: "0 0 0.125rem #000000, 0.125rem 0 0.125rem #000000, -0.125rem 0 0.125rem #000000, 0 0.125rem 0.125rem #000000, -0.125rem 0 0.125rem #000000",

                    div {
                        line_height: 1,
                        white_space: "pre",
                        title: "{money:.2} рублей",
                        {format_money(money, "\n")}
                    }

                    div {
                        margin_top: "1rem",
                        font_size: "1.5rem",
                        "Скорость: " {format_money(click_increment * base_rate as f64, " ")} "/сек"
                    }
                }

                div {
                    flex: "0 0 20rem",

                    display: "flex",
                    align_items: "center",

                    img {
                        style: "height: 16rem;",
                        box_shadow: "0 0 2rem 2rem #ffffff80",
                        border_radius: if COINS[stage].is_circular { "50%" } else { "0" },
                        animation: {
                            if clicks() == 0 {
                                ""
                            } else if clicks() % 2 == 0 {
                                "coin-click-1 0.3s ease-in"
                            } else {
                                "coin-click-2 0.3s ease-in"
                            }
                        },
                        cursor: "pointer",
                        draggable: false,
                        onclick: move |event| async move {
                            clicks += 1;
                            progress.write().money += click_increment;
                            click_positions.write().push_back((event.data.client_coordinates().to_tuple(), clicks(), click_increment));
                            tokio::time::sleep(Duration::from_millis(1000)).await;
                            click_positions.write().pop_front();
                        },

                        src: COINS[stage].icon,
                    }
                }

                footer {
                    flex: "1 1 0",
                }
            }

            aside {
                flex: "0 0 24rem",

                display: "flex",
                flex_direction: "column",
                justify_content: "center",

                h2 {
                    text_align: "center",
                    "Моющие средства"
                }

                for (i, (washer, count)) in WASHERS.iter().zip(washer_counts).enumerate() {
                    BuyWasher {
                        washer,
                        count,
                        money,
                        click_increment,
                        onbuy: move |cost| {
                            let mut progress = progress.write();
                            progress.money -= cost;
                            progress.washer_counts[i] += 1;
                            progress.base_rate += washer.base_rate;
                        }
                    }
                }
            }
        }

        for ((x, y), key, increment) in click_positions() {
            div {
                key: "{key}",

                position: "fixed",
                left: "{x}px",
                top: "{y}px",

                font_size: "1.5rem",
                color: "#40ff40",

                animation: "click-trace 1s linear",

                pointer_events: "none",

                "+ {increment}"
            }
        }
    }
}

#[component]
fn BuyWasher(
    washer: &'static Washer,
    count: u64,
    money: f64,
    click_increment: f64,
    onbuy: EventHandler<f64>,
) -> Element {
    let cost = (washer.cost * 1.5f64.powf(count as f64) * 100.0).ceil() / 100.0;
    let can_buy = money >= cost;

    rsx! {
        div {
            display: "flex",
            flex_direction: "row",
            align_items: "center",
            margin_bottom: "1rem",
            padding: "0.25rem 0.125rem",

            cursor: if can_buy {
                "pointer"
            } else {
                "not-allowed"
            },
            background_color: if can_buy {
                "#80ff0040"
            } else {
                "#ff800040"
            },

            onclick: move |_event| {
                if can_buy {
                    onbuy.call(cost);
                }
            },

            div {
                flex: "0 0 4rem",
                width: "4rem",
                height: "4rem",
                position: "relative",
                background_image: "url({washer.icon})",
                background_position: "center",
                background_size: "contain",
                background_repeat: "no-repeat",

                if count > 0 {
                    div {
                        position: "absolute",
                        right: "-0.75rem",
                        bottom: "-0.5rem",

                        display: "flex",
                        align_items: "center",
                        justify_content: "center",

                        width: "1.75rem",
                        height: "1.75rem",
                        border_radius: "50%",
                        background_color: "#f02020",

                        font_size: "0.75rem",
                        white_space: "nowrap",

                        "×{count}"
                    }
                }
            }

            div {
                margin_left: "1rem",

                div {
                    font_size: "1.5rem",
                    margin_bottom: "0.25rem",

                    {washer.name}
                }

                div {
                    "Скорость: " {format_money(click_increment * washer.base_rate as f64, " ")} "/сек"
                }

                div {
                    "Цена: " {format_money(cost, " ")}
                }
            }
        }
    }
}
