use anyhow::{ensure, Context, Result};
use core::marker::Unpin;
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::{TcpListener, TcpStream, UnixStream};

async fn wide_to_byte(
    mut rx: impl AsyncReadExt + Unpin,
    mut tx: impl AsyncWriteExt + Unpin,
) -> Result<()> {
    let mut buf = [0u8; 256];
    loop {
        let byte = rx.read(&mut buf).await?;
        if byte == 0 {
            return Ok(());
        }
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
        ensure!(byte == tx.write(&vec![0; byte]).await?, "send");
        tx.flush().await?;
        tokio::time::sleep(core::time::Duration::from_millis(200)).await;
    }
}

async fn handle(mut sock: TcpStream) -> Result<()> {
    let (tcp_rx, tcp_tx) = sock.split();

    let mut unix = UnixStream::connect("/tmp/internal.sock")
        .await
        .context("unix conn")?;
    let (unix_rx, unix_tx) = unix.split();

    let (ttu, utt) = tokio::join!(wide_to_byte(tcp_rx, unix_tx), byte_to_wide(unix_rx, tcp_tx));
    ttu.context("wide -> byte")?;
    utt.context("byte -> wide")?;

    Ok(())
}

#[tokio::main]
async fn main() -> Result<()> {
    let listener = TcpListener::bind("0.0.0.0:3252").await.context("bind")?;
    eprintln!("Listening on 0.0.0.0:3252 proxying to unix:/tmp/internal.sock");
    loop {
        let (sock, _addr) = listener.accept().await.context("accept")?;
        tokio::spawn(handle(sock));
    }
}
