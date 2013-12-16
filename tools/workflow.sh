#cur_dir=$(cd "$(dirname "$0")"; pwd)
cd "$(dirname "$0")"

#echo $PWD
python proxy_downloader.py > /dev/null 2>&1
python proxy_verifier.py > /dev/null 2>&1
