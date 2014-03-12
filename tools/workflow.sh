#cur_dir=$(cd "$(dirname "$0")"; pwd)
cd "$(dirname "$0")"

export PATH=/usr/local/bin:$PATH
#echo $PWD
python proxy_downloader.py > /dev/null 2>&1
python proxy_verifier.py > /dev/null 2>&1
#mysql -h192.168.0.57 -uproduct_r -pproduct_r proxy -e "select concat('http://', ip, ':', cast(port as char)) from proxy_hidemyass where kxflag in ('good', 'moderate') and country = 'China' " | sed -n '2,$p' > proxy_list.txt 2>/dev/null
