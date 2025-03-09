use crate::assets::{asset, Asset};
use dioxus::prelude::*;

pub struct Coin {
    pub value: f64,
    pub icon: Asset,
    pub goal_text: &'static str,
    pub cost: f64,
    pub is_circular: bool,
}

pub const COINS: &[Coin] = &[
    Coin {
        value: 0.01,
        icon: asset!("/assets/coins/1c.avif"),
        goal_text: "",
        cost: 0.0,
        is_circular: true,
    },
    Coin {
        value: 0.05,
        icon: asset!("/assets/coins/5c.avif"),
        goal_text: "Поискать под плинтусом",
        cost: 1e1,
        is_circular: true,
    },
    Coin {
        value: 0.1,
        icon: asset!("/assets/coins/10c.avif"),
        goal_text: "Разбить копилку",
        cost: 1e2,
        is_circular: true,
    },
    Coin {
        value: 0.5,
        icon: asset!("/assets/coins/50c.avif"),
        goal_text: "Выдернуть зубы для зубной феи",
        cost: 1e3,
        is_circular: true,
    },
    Coin {
        value: 1.0,
        icon: asset!("/assets/coins/1.avif"),
        goal_text: "Попросить милостыню",
        cost: 1e4,
        is_circular: true,
    },
    Coin {
        value: 2.0,
        icon: asset!("/assets/coins/2.avif"),
        goal_text: "Сыграть в переходе",
        cost: 1e5,
        is_circular: true,
    },
    Coin {
        value: 5.0,
        icon: asset!("/assets/coins/5.avif"),
        goal_text: "Поднять с тротуара",
        cost: 1e6,
        is_circular: true,
    },
    Coin {
        value: 10.0,
        icon: asset!("/assets/coins/10.avif"),
        goal_text: "Попросить у мамы",
        cost: 1e7,
        is_circular: true,
    },
    Coin {
        value: 50.0,
        icon: asset!("/assets/coins/50.avif"),
        goal_text: "Собрать билеты банка приколов",
        cost: 1e8,
        is_circular: false,
    },
    Coin {
        value: 100.0,
        icon: asset!("/assets/coins/100.avif"),
        goal_text: "Помочь другу на контрольной",
        cost: 1e9,
        is_circular: false,
    },
    Coin {
        value: 200.0,
        icon: asset!("/assets/coins/200.avif"),
        goal_text: "Помайнить Bitcoin",
        cost: 1e10,
        is_circular: false,
    },
    Coin {
        value: 500.0,
        icon: asset!("/assets/coins/500.avif"),
        goal_text: "Продать PlayStation брата",
        cost: 1e11,
        is_circular: false,
    },
    Coin {
        value: 1000.0,
        icon: asset!("/assets/coins/1000.avif"),
        goal_text: "Порыться в зимней куртке",
        cost: 1e12,
        is_circular: false,
    },
    Coin {
        value: 2000.0,
        icon: asset!("/assets/coins/2000.avif"),
        goal_text: "Найти клад",
        cost: 1e13,
        is_circular: false,
    },
    Coin {
        value: 5000.0,
        icon: asset!("/assets/coins/5000.avif"),
        goal_text: "Распечатать с Википедии",
        cost: 1e14,
        is_circular: false,
    },
    Coin {
        value: 0.0,
        icon: asset!("/assets/coins/flag.avif"),
        goal_text: "Купить флаг",
        cost: 1e15,
        is_circular: false,
    },
];

#[derive(PartialEq)]
pub struct Washer {
    pub base_rate: u64,
    pub icon: Asset,
    pub name: &'static str,
    pub cost: f64,
}

pub const WASHERS: &[Washer] = &[
    Washer {
        base_rate: 1,
        icon: asset!("/assets/washers/toothbrush.avif"),
        name: "Зубная щётка",
        cost: 0.2,
    },
    Washer {
        base_rate: 20,
        icon: asset!("/assets/washers/sponge.avif"),
        name: "Губка для посуды",
        cost: 10.0,
    },
    Washer {
        base_rate: 200,
        icon: asset!("/assets/washers/dishwasher.avif"),
        name: "Посудомойка",
        cost: 500.0,
    },
    Washer {
        base_rate: 500,
        icon: asset!("/assets/washers/washingmachine.avif"),
        name: "Стиральная машина",
        cost: 10000.0,
    },
];
