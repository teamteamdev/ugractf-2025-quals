<?php
// A slight modification of https://github.com/Rouji/single_php_filehost
//
// > Copyright © 2021, Andreas Hackl <a@r0.at>
// >
// > Permission to use, copy, modify, and/or distribute this software for any
// > purpose with or  without fee is hereby granted,  provided that the above
// > copyright notice and this permission notice appear in all copies.
// >
// > THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
// > WITH  REGARD  TO  THIS  SOFTWARE  INCLUDING  ALL  IMPLIED  WARRANTIES OF
// > MERCHANTABILITY AND FITNESS.  IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
// > ANY SPECIAL,  DIRECT,  INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
// > WHATSOEVER RESULTING  FROM LOSS OF USE,  DATA OR PROFITS,  WHETHER IN AN
// > ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
// > OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

class CONFIG
{
    const MAX_FILESIZE = 1; //max. filesize in MiB

    const ID_LENGTH = 10; //length of the random file ID
    const STORE_PATH = '/tmp/uploads/'; //directory to store uploaded files in
    const DOWNLOAD_PATH = 'files/%s'; //the path part of the download url. %s = placeholder for filename
    const MAX_EXT_LEN = 7; //max. length for file extensions
    const AUTO_FILE_EXT = false; //automatically try to detect file extension for files that have none

    public static function SITE_URL() : string
    {
        return "https://{$_SERVER['HTTP_HOST']}/{$_SERVER['HTTP_X_TOKEN']}";
    }

    public static function SCRIPT_URL() : string
    {
        return CONFIG::SITE_URL().$_SERVER['REQUEST_URI'];
    }
};


// generate a random string of characters with given length
function rnd_str(int $len) : string
{
    $chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_';
    $max_idx = strlen($chars) - 1;
    $out = '';
    while ($len--)
    {
        $out .= $chars[mt_rand(0,$max_idx)];
    }
    return $out;
}

//extract extension from a path (does not include the dot)
function ext_by_path(string $path) : string
{
    $ext = pathinfo($path, PATHINFO_EXTENSION);
    //special handling of .tar.* archives
    $ext2 = pathinfo(substr($path,0,-(strlen($ext)+1)), PATHINFO_EXTENSION);
    if ($ext2 === 'tar')
    {
        $ext = $ext2.'.'.$ext;
    }
    return $ext;
}

function ext_by_finfo(string $path) : string
{
    $finfo = finfo_open(FILEINFO_EXTENSION);
    $finfo_ext = finfo_file($finfo, $path);
    finfo_close($finfo);
    if ($finfo_ext != '???')
    {
        return explode('/', $finfo_ext, 2)[0];
    }
    else
    {
        $finfo = finfo_open();
        $finfo_info = finfo_file($finfo, $path);
        finfo_close($finfo);
        if (strstr($finfo_info, 'text') !== false)
        {
            return 'txt';
        }
    }
    return '';
}

// store an uploaded file, given its name and temporary path (e.g. values straight out of $_FILES)
// files are stored wit a randomised name, but with their original extension
//
// $name: original filename
// $tmpfile: temporary path of uploaded file
// $formatted: set to true to display formatted message instead of bare link
function store_file(string $name, string $tmpfile, bool $formatted = false) : void
{
    //create folder, if it doesn't exist
    if (!file_exists(CONFIG::STORE_PATH))
    {
        mkdir(CONFIG::STORE_PATH, 0750, true); //TODO: error handling
    }

    //check file size
    $size = filesize($tmpfile);
    if ($size > CONFIG::MAX_FILESIZE * 1024 * 1024)
    {
        header('HTTP/1.0 413 Payload Too Large');
        print("Error 413: Max File Size ({CONFIG::MAX_FILESIZE} MiB) Exceeded\n");
        return;
    }
    if ($size == 0)
    {
        header('HTTP/1.0 400 Bad Request');
        print('Error 400: Uploaded file is empty\n');
        return;
    }

    $ext = ext_by_path($name);
    if (empty($ext) && CONFIG::AUTO_FILE_EXT)
    {
        $ext = ext_by_finfo($tmpfile);
    }
    $ext = substr($ext, 0, CONFIG::MAX_EXT_LEN);
    $tries_per_len=3; //try random names a few times before upping the length

    for ($len = CONFIG::ID_LENGTH; ; ++$len)
    {
        for ($n=0; $n<=$tries_per_len; ++$n)
        {
            $id = rnd_str($len);
            $basename = $id . (empty($ext) ? '' : '.' . $ext);
            $target_file = CONFIG::STORE_PATH . $basename;

            if (!file_exists($target_file))
                break 2;
        }
    }

    $res = move_uploaded_file($tmpfile, $target_file);
    if (!$res)
    {
        //TODO: proper error handling?
        header('HTTP/1.0 520 Unknown Error');
        return;
    }

    //print the download link of the file
    $url = sprintf(CONFIG::SITE_URL().'/'.CONFIG::DOWNLOAD_PATH, $basename);

    print("$url\n");
}

function send_text_file(string $filename, string $content) : void
{
    header('Content-type: application/octet-stream');
    header("Content-Disposition: attachment; filename=\"$filename\"");
    header('Content-Length: '.strlen($content));
    print($content);
}

// print a plaintext info page, explaining what this script does and how to
// use it, how to upload, etc.
function print_index() : void
{
    $site_url = CONFIG::SCRIPT_URL();

echo <<<EOT
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Pastebin</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>
        html {
            height: 100%;
        }

        body {
            font-family: monospace;
            margin: 0;
            box-sizing: border-box;
            display: flex;
            height: 100%;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }

        @media (prefers-color-scheme: dark) {
            body {
                background: #111;
                color: #ddd;
            }
        }
    </style>
</head>
<body>

<h1>Pastebin</h1>
curl -F "file=@/path/to/your/file.jpg" $site_url

</body>
</html>
EOT;
}


// decide what to do, based on POST parameters etc.
if (isset($_FILES['file']['name']) &&
    isset($_FILES['file']['tmp_name']) &&
    is_uploaded_file($_FILES['file']['tmp_name']))
{
    //file was uploaded, store it
    $formatted = isset($_REQUEST['formatted']);
    store_file($_FILES['file']['name'],
              $_FILES['file']['tmp_name'],
              $formatted);
}
else
{
    print_index();
}
