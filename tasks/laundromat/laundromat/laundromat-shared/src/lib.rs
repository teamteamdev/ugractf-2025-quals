use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, Default, PartialEq, Deserialize, Serialize)]
pub struct Progress {
    pub money: f64,
    pub base_rate: u64,
    pub stage: usize,
    pub washer_counts: Vec<u64>,
}

#[derive(Debug, Deserialize, Serialize)]
pub enum Request {
    Authorize(String),
    Load,
    Save(Progress),
    Flag(FlagMagic),
}

#[derive(Serialize)]
#[serde(untagged)]
pub enum Response {
    Authorize(()),
    Load(Progress),
    Save(()),
    Flag(String),
}

#[derive(Clone, Copy, Debug, PartialEq, Deserialize, Serialize)]
pub struct FlagMagic(f64, pub u64, f64, u64);

pub const FLAG_MAGIC: FlagMagic = FlagMagic(
    0.7948312570714565,
    11778552145163962679,
    0.15677558204784214,
    16914467128761609130,
);
