#[cfg(not(feature = "bundle"))]
mod imp {
    pub use dioxus::prelude::{asset, Asset};

    pub fn read_asset(path: &str) -> Vec<u8> {
        std::fs::read(format!("{}{}", env!("CARGO_MANIFEST_DIR"), path)).expect("asset missing")
    }
}

#[cfg(feature = "bundle")]
mod imp {
    use std::io::{Cursor, Read};
    use std::sync::LazyLock;
    use zip::ZipArchive;

    #[derive(Clone, Copy, PartialEq)]
    pub struct Asset {
        pub url: &'static str,
    }

    #[link_section = ".вложения"]
    static ASSETS_ZIP_SECTION: [u8; include_bytes!(env!("ASSETS_ZIP")).len()] =
        *include_bytes!(env!("ASSETS_ZIP"));

    const ASSETS_ZIP: LazyLock<ZipArchive<Cursor<&[u8]>>> = LazyLock::new(|| {
        ZipArchive::new(Cursor::new(&ASSETS_ZIP_SECTION as &[u8]))
            .expect("failed to parse asset ZIP")
    });

    impl std::fmt::Display for Asset {
        fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
            write!(f, "{}", self.url)
        }
    }

    impl From<Asset> for String {
        fn from(value: Asset) -> Self {
            value.to_string()
        }
    }

    impl From<Asset> for Option<String> {
        fn from(value: Asset) -> Self {
            Some(value.to_string())
        }
    }

    impl dioxus_core_types::DioxusFormattable for Asset {
        fn format(&self) -> std::borrow::Cow<'static, str> {
            self.url.into()
        }
    }

    macro_rules! asset {
        ($path:literal) => {
            $crate::assets::Asset {
                url: concat!("laundromat:/", $path),
            }
        };
    }
    pub(crate) use asset;

    pub fn read_asset(path: &str) -> Vec<u8> {
        let mut data = Vec::new();
        (*ASSETS_ZIP)
            .clone()
            .by_name(path.strip_prefix("/").expect("missing / prefix"))
            .expect("asset not found")
            .read_to_end(&mut data)
            .expect("failed to read asset");
        data
    }
}

pub use imp::*;
