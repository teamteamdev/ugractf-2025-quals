use laundromat_shared::{FlagMagic, Progress, Request};
use rustls::{ClientConfig, ClientConnection, RootCertStore, StreamOwned};
use rustls_pki_types::ServerName;
use serde::de::DeserializeOwned;
use std::error::Error;
use std::io::Write;
use std::net::TcpStream;
use std::sync::Arc;

pub struct Communicator {
    stream: StreamOwned<ClientConnection, TcpStream>,
}

impl Communicator {
    pub fn connect() -> Result<Self, Box<dyn Error + Send + Sync>> {
        let root_cert_store = RootCertStore {
            roots: webpki_roots::TLS_SERVER_ROOTS.into(),
        };
        let config = ClientConfig::builder()
            .with_root_certificates(root_cert_store)
            .with_no_client_auth();

        let server_name = ServerName::try_from("laundromat.q.2025.ugractf.ru").unwrap();
        let connection = ClientConnection::new(Arc::new(config), server_name).unwrap();

        let socket = TcpStream::connect("laundromat.q.2025.ugractf.ru:3255")?;

        Ok(Self {
            stream: StreamOwned::new(connection, socket),
        })
    }

    fn request<T: DeserializeOwned>(
        &mut self,
        request: Request,
    ) -> Result<T, Box<dyn Error + Send + Sync>> {
        let mut encoded_request = Vec::new();
        ciborium::into_writer(&request, &mut encoded_request)?;
        self.stream.write_all(&encoded_request)?;
        Ok(ciborium::from_reader(&mut self.stream)?)
    }

    pub fn authorize(&mut self, token: String) -> Result<(), Box<dyn Error + Send + Sync>> {
        self.request(Request::Authorize(token))
    }

    pub fn load(&mut self) -> Result<Progress, Box<dyn Error + Send + Sync>> {
        self.request(Request::Load)
    }

    pub fn save(&mut self, progress: Progress) -> Result<(), Box<dyn Error + Send + Sync>> {
        self.request(Request::Save(progress))
    }

    // Prevent easy jmp overrides
    #[inline(always)]
    pub fn get_flag(&mut self, magic: FlagMagic) -> Result<String, Box<dyn Error + Send + Sync>> {
        self.request(Request::Flag(magic))
    }
}
