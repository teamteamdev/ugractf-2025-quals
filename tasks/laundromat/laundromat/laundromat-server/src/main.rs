use laundromat_shared::{FLAG_MAGIC, Progress, Request, Response};
use std::error::Error;
use std::fs::{File, Permissions};
use std::io::ErrorKind;
use std::os::unix::fs::PermissionsExt;
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::UnixListener;

struct Client {
    token: String,
    flag: String,
}

impl Client {
    fn new() -> Self {
        Self {
            token: String::new(),
            flag: String::new(),
        }
    }

    async fn authorize(&mut self, token: String) {
        assert!(
            token.len() == 16 && token.chars().all(char::is_alphanumeric),
            "invalid token format",
        );
        let response = reqwest::get(format!("http://127.0.0.1:54327/{token}"))
            .await
            .expect("failed to connect to secret service");
        match response.status() {
            reqwest::StatusCode::OK => {
                self.flag = response
                    .text()
                    .await
                    .expect("failed to receive flag from secret service");
            }
            reqwest::StatusCode::FORBIDDEN => {
                panic!("incorrect token");
            }
            status_code => {
                panic!("unexpected status code {status_code} from secret service");
            }
        }
        self.token = token;
    }

    fn load(&self) -> Progress {
        assert!(!self.token.is_empty(), "not authorized");
        match File::open(format!("/state/{}", self.token)) {
            Ok(file) => ciborium::from_reader(file).expect("invalid state on disk"),
            Err(e) if e.kind() == ErrorKind::NotFound => Default::default(),
            Err(e) => {
                panic!("unknown error while reading state: {e}");
            }
        }
    }

    fn save(&self, progress: Progress) {
        assert!(!self.token.is_empty(), "not authorized");
        ciborium::into_writer(
            &progress,
            File::create(format!("/state/{}.tmp", self.token)).expect("failed to create file"),
        )
        .expect("failed to save state");
        std::fs::rename(
            format!("/state/{}.tmp", self.token),
            format!("/state/{}", self.token),
        )
        .expect("failed to commit state");
    }

    async fn handle_request(&mut self, request: Request) -> Response {
        println!("{request:?}");

        match request {
            Request::Authorize(token) => {
                self.authorize(token).await;
                Response::Authorize(())
            }

            Request::Load => Response::Load(self.load()),

            Request::Save(progress) => {
                self.save(progress);
                Response::Save(())
            }

            Request::Flag(magic) => {
                assert!(!self.token.is_empty(), "not authorized");
                assert!(magic == FLAG_MAGIC, "incorrect flag magic");
                Response::Flag(self.flag.clone())
            }
        }
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    let listener = UnixListener::bind("/tmp/server.sock")?;
    std::fs::set_permissions("/tmp/server.sock", Permissions::from_mode(0o666))?;

    loop {
        let (mut socket, _) = listener.accept().await?;
        eprintln!("New connection");

        tokio::spawn(async move {
            let mut client = Client::new();

            let mut buffer = [0; 1024];
            let mut taken_len = 0;

            loop {
                assert!(taken_len < buffer.len(), "buffer full, assuming DoS");

                let n = socket
                    .read(&mut buffer[taken_len..])
                    .await
                    .expect("failed to read data from socket");
                assert!(n > 0, "EOF on socket");

                taken_len += n;

                let mut cursor = &buffer[..taken_len];
                match ciborium::from_reader(&mut cursor) {
                    Ok(request) => {
                        let n_read = taken_len - cursor.len();
                        buffer.copy_within(n_read..taken_len, 0);
                        taken_len -= n_read;

                        let mut response = Vec::new();
                        ciborium::into_writer(&client.handle_request(request).await, &mut response)
                            .expect("failed to serialize response");
                        socket
                            .write_all(&response)
                            .await
                            .expect("failed to write data to socket");
                    }

                    Err(ciborium::de::Error::Io(e)) if e.kind() == ErrorKind::UnexpectedEof => {
                        // Keep reading
                    }

                    Err(e) => {
                        panic!("{e:?}");
                    }
                }
            }
        });
    }
}
