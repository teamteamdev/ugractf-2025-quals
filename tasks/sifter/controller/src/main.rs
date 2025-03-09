#![feature(integer_sign_cast)]

use axum::Router;
use axum::extract::ws::{Message, WebSocket, WebSocketUpgrade};
use axum::response::IntoResponse;
use axum::routing::any;
use rustix::fs::Mode;
use serde::{Deserialize, Serialize};
use std::collections::VecDeque;
use std::sync::LazyLock;
use tokio::net::UnixListener;
use tower_http::services::ServeFile;
use tower_http::trace::TraceLayer;
use tracing_subscriber::layer::SubscriberExt;
use tracing_subscriber::util::SubscriberInitExt;

#[derive(Serialize)]
pub enum InsnError {
    Undefined,
    Halt,
    InputRequested,
}

pub type InsnResult<T = ()> = Result<T, InsnError>;

#[derive(Serialize, Deserialize)]
pub struct State {
    #[serde(with = "serde_big_array::BigArray")]
    pub mem: [u8; 256],
    pub reg: [u8; 4],
    pub zero: bool,
    pub sign: bool,
    pub carry: bool,
    pub overflow: bool,
    pub pc: u8,

    pub input: VecDeque<u8>,
    pub output: Vec<u8>,
}

impl State {
    pub fn make(flag: [u8; 48]) -> State {
        // std::fs::read("/task/controller/prog.o").unwrap().try_into().unwrap()
        let mut mem: [u8; 256] = *include_bytes!("../prog.o");
        for (dst, src) in mem[0xc5..0xf5].iter_mut().zip(flag) {
            *dst ^= src;
        }

        State {
            mem,
            reg: [0; 4],
            zero: false,
            sign: false,
            carry: false,
            overflow: false,
            pc: 0,

            input: VecDeque::new(),
            output: vec![],
        }
    }

    #[inline]
    pub fn step(&mut self) -> InsnResult {
        (INSTRUCTIONS[self.mem[self.pc as usize] as usize])(self)
    }

    // No more than a few insns
    pub fn run(&mut self) -> InsnResult {
        for _ in 0..4000 {
            self.step()?;
        }
        Ok(())
    }
}

mod imp {
    use super::{InsnError, InsnResult, State};

    #[inline]
    fn advance(st: &mut State) {
        st.pc = st.pc.wrapping_add(1)
    }

    #[inline]
    fn src_dst(st: &State) -> (u8, u8) {
        let insn = st.mem[st.pc as usize];
        (insn % 16 / 4, insn % 4)
    }

    #[inline]
    fn arg(st: &State) -> u8 {
        let insn = st.mem[st.pc as usize];
        insn % 4
    }

    #[inline]
    fn cc(st: &State) -> u8 {
        let insn = st.mem[st.pc as usize];
        insn % 16
    }

    #[inline]
    fn get_imm(st: &State) -> u8 {
        st.mem[st.pc.wrapping_add(1) as usize]
    }

    pub fn mov(st: &mut State) -> InsnResult {
        let (src, dst) = src_dst(st);
        st.reg[dst as usize] = st.reg[src as usize];
        advance(st);
        Ok(())
    }

    pub fn add(st: &mut State) -> InsnResult {
        let (src, dst) = src_dst(st);
        st.reg[dst as usize] = st.reg[dst as usize].wrapping_add(st.reg[src as usize]);
        advance(st);
        Ok(())
    }

    pub fn xor(st: &mut State) -> InsnResult {
        let (src, dst) = src_dst(st);
        st.reg[dst as usize] ^= st.reg[src as usize];
        advance(st);
        Ok(())
    }

    pub fn and(st: &mut State) -> InsnResult {
        let (src, dst) = src_dst(st);
        st.reg[dst as usize] &= st.reg[src as usize];
        advance(st);
        Ok(())
    }

    pub fn ldw(st: &mut State) -> InsnResult {
        let (src, dst) = src_dst(st);
        st.reg[dst as usize] = st.mem[st.reg[src as usize] as usize];
        advance(st);
        Ok(())
    }

    pub fn stw(st: &mut State) -> InsnResult {
        let (src, dst) = src_dst(st);
        st.mem[st.reg[dst as usize] as usize] = st.reg[src as usize];
        advance(st);
        Ok(())
    }

    pub fn cmp(st: &mut State) -> InsnResult {
        let (src, dst) = src_dst(st);
        let src = st.reg[src as usize];
        let dst = st.reg[dst as usize];
        st.zero = src == dst;
        st.sign = dst.wrapping_sub(src).cast_signed() < 0;
        st.carry = dst < src;
        st.overflow = dst.wrapping_sub(src).cast_signed() as i16
            != dst.cast_signed() as i16 - src.cast_signed() as i16;
        advance(st);
        Ok(())
    }

    pub fn orr(st: &mut State) -> InsnResult {
        let (src, dst) = src_dst(st);
        st.reg[dst as usize] |= st.reg[src as usize];
        advance(st);
        Ok(())
    }

    pub fn imm(st: &mut State) -> InsnResult {
        let arg = arg(st) as usize;
        st.reg[arg] = get_imm(st);
        advance(st);
        advance(st);
        Ok(())
    }

    pub fn neg(st: &mut State) -> InsnResult {
        let arg = arg(st) as usize;
        st.reg[arg] = st.reg[arg].wrapping_neg();
        advance(st);
        Ok(())
    }

    pub fn com(st: &mut State) -> InsnResult {
        let arg = arg(st) as usize;
        st.reg[arg] = !st.reg[arg];
        advance(st);
        Ok(())
    }

    pub fn shl(st: &mut State) -> InsnResult {
        let arg = arg(st) as usize;
        st.reg[arg] = st.reg[arg].wrapping_shl(1);
        advance(st);
        Ok(())
    }

    pub fn inn(st: &mut State) -> InsnResult {
        st.reg[arg(st) as usize] = st.input.pop_front().ok_or(InsnError::InputRequested)?;
        advance(st);
        Ok(())
    }

    pub fn out(st: &mut State) -> InsnResult {
        st.output.push(st.reg[arg(st) as usize]);
        advance(st);
        Ok(())
    }

    pub fn tst(st: &mut State) -> InsnResult {
        let arg = st.reg[arg(st) as usize];
        st.zero = arg == 0;
        st.sign = arg.cast_signed() < 0;
        st.carry = false;
        st.overflow = false;
        advance(st);
        Ok(())
    }

    pub fn rbt(st: &mut State) -> InsnResult {
        let arg = arg(st) as usize;
        st.reg[arg] = st.reg[arg].reverse_bits();
        advance(st);
        Ok(())
    }

    pub fn shr(st: &mut State) -> InsnResult {
        let arg = arg(st) as usize;
        st.reg[arg] = st.reg[arg].wrapping_shr(get_imm(st).into());
        advance(st);
        advance(st);
        Ok(())
    }

    pub fn sar(st: &mut State) -> InsnResult {
        let arg = arg(st) as usize;
        st.reg[arg] = st.reg[arg]
            .cast_signed()
            .wrapping_shr(get_imm(st).into())
            .cast_unsigned();
        advance(st);
        advance(st);
        Ok(())
    }

    pub fn rol(st: &mut State) -> InsnResult {
        let arg = arg(st) as usize;
        st.reg[arg] = st.reg[arg].rotate_left(get_imm(st).into());
        advance(st);
        advance(st);
        Ok(())
    }

    pub fn ror(st: &mut State) -> InsnResult {
        let arg = arg(st) as usize;
        st.reg[arg] = st.reg[arg].rotate_right(get_imm(st).into());
        advance(st);
        advance(st);
        Ok(())
    }

    pub fn jcc(st: &mut State) -> InsnResult {
        let cc = cc(st);
        let flip = cc / 8 == 1;

        let taken = match cc % 8 {
            0 => true,
            1 => st.sign != st.overflow,
            2 => st.zero || st.carry,
            3 => st.zero || (st.sign != st.overflow),
            4 => st.zero,
            5 => st.sign,
            6 => st.carry,
            7 => st.overflow,
            _ => unreachable!(),
        };

        if taken != flip {
            // taken
            st.pc = get_imm(st);
        } else {
            // skipped
            advance(st);
            advance(st);
        }
        Ok(())
    }

    pub fn inc(st: &mut State) -> InsnResult {
        let arg = arg(st) as usize;
        st.reg[arg] = st.reg[arg].wrapping_add(1);
        advance(st);
        Ok(())
    }

    pub fn dec(st: &mut State) -> InsnResult {
        let arg = arg(st) as usize;
        st.reg[arg] = st.reg[arg].wrapping_sub(1);
        advance(st);
        Ok(())
    }

    pub fn und(_st: &mut State) -> InsnResult {
        Err(InsnError::Undefined)
    }

    pub fn hlt(_st: &mut State) -> InsnResult {
        Err(InsnError::Halt)
    }
}

type Insn = fn(&mut State) -> InsnResult;
static INSTRUCTIONS: LazyLock<[Insn; 256]> = LazyLock::new(|| {
    use imp::*;

    let mut res = Vec::<Insn>::new();

    // 0... ....
    res.extend([mov as Insn; 16]);
    res.extend([add as Insn; 16]);
    res.extend([xor as Insn; 16]);
    res.extend([and as Insn; 16]);
    res.extend([ldw as Insn; 16]);
    res.extend([stw as Insn; 16]);
    res.extend([cmp as Insn; 16]);
    res.extend([orr as Insn; 16]);

    // 1000 ....
    res.extend([imm as Insn; 4]);
    res.extend([neg as Insn; 4]);
    res.extend([com as Insn; 4]);
    res.extend([shl as Insn; 4]);

    // 1001 ....
    res.extend([inn as Insn; 4]);
    res.extend([out as Insn; 4]);
    res.extend([tst as Insn; 4]);
    res.extend([rbt as Insn; 4]);

    // 1010 ....
    res.extend([shr as Insn; 4]);
    res.extend([sar as Insn; 4]);
    res.extend([rol as Insn; 4]);
    res.extend([ror as Insn; 4]);

    // 1011 ....
    res.extend([jcc as Insn; 16]);

    // 1100 0...
    res.extend([inc as Insn; 4]);
    res.extend([dec as Insn; 4]);

    // 1100 1...
    res.extend([und as Insn; 8]);
    // 1101 ....
    res.extend([und as Insn; 16]);
    // 111. ....
    res.extend([und as Insn; 31]);
    // 1111 1111
    res.extend([hlt as Insn; 1]);

    res.try_into().unwrap()
});

#[tokio::main]
async fn main() -> std::io::Result<()> {
    tracing_subscriber::registry()
        .with(
            tracing_subscriber::EnvFilter::try_from_default_env().unwrap_or_else(|_| {
                format!("{}=debug,tower_http=debug", env!("CARGO_CRATE_NAME")).into()
            }),
        )
        .with(tracing_subscriber::fmt::layer())
        .init();

    let app = Router::new()
        .route_service(
            "/{token}",
            ServeFile::new("/task/controller/static/index.html"),
        )
        .route("/ws", any(ws_handler))
        .layer(TraceLayer::new_for_http());

    let listener = UnixListener::bind("/tmp/external.sock")?;
    rustix::fs::chmod("/tmp/external.sock", Mode::from_raw_mode(0o666))?;
    tracing::debug!("listening on {:?}", listener.local_addr());
    axum::serve(listener, app).await
}

async fn ws_handler(ws: WebSocketUpgrade) -> impl IntoResponse {
    ws.on_upgrade(handle_socket)
}

#[derive(Deserialize)]
struct Command {
    single_step: bool,
    state: State,
}

async fn get_flag_by_token(token: &str) -> Result<String, String> {
    if token.len() != 16 || !token.chars().all(char::is_alphanumeric) {
        Err("invalid token format")?
    }
    let Ok(response) = reqwest::get(format!("http://127.0.0.1:54327/{token}")).await else {
        Err("token validator is dead")?
    };
    match response.status() {
        reqwest::StatusCode::OK => {
            let Ok(flag) = response.text().await else {
                Err("failed to receive flag from secret service")?
            };
            Ok(flag)
        }
        reqwest::StatusCode::FORBIDDEN => Err("incorrect token")?,
        status_code => Err(format!("internal server error {status_code}"))?,
    }
}

async fn handle_socket(mut ws: WebSocket) {
    let Some(Ok(Message::Text(token))) = ws.recv().await else {
        return;
    };

    let maybe_flag = get_flag_by_token(token.as_str()).await;
    ws.send(Message::Text(
        serde_json::to_string(&maybe_flag.as_ref().map(drop))
            .unwrap()
            .into(),
    ))
    .await
    .unwrap();

    let Ok(flag) = maybe_flag else { return };
    let flag = format!("{flag}\n")
        .into_bytes()
        .try_into()
        .expect("unexpected flag length");
    ws.send(Message::Text(
        serde_json::to_string(&(Ok::<_, ()>(()), State::make(flag)))
            .unwrap()
            .into(),
    ))
    .await
    .unwrap();

    loop {
        let message = tokio::time::timeout(core::time::Duration::from_secs(10), ws.recv()).await;
        let msg = match message {
            Err(_) => {
                ws.send(Message::Pong("keepalive".into())).await.unwrap();
                continue;
            }
            Ok(Some(Ok(Message::Text(msg)))) => msg,
            Ok(_) => break,
        };

        let Ok(Command {
            single_step,
            mut state,
        }) = serde_json::from_str(msg.as_str())
        else {
            break;
        };

        let result = if single_step {
            state.step()
        } else {
            state.run()
        };

        ws.send(Message::Text(
            serde_json::to_string(&(result, state)).unwrap().into(),
        ))
        .await
        .unwrap();
    }
}
