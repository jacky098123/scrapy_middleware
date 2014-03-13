#cur_dir=$(cd "$(dirname "$0")"; pwd)
cd "$(dirname "$0")"

export PATH=/usr/local/bin:$PATH
mysql -h192.168.0.57 -uproduct_r -pproduct_r proxy -e "select concat('http://', ip, ':', cast(port as char)) from proxy_hidemyass where kxflag in ('good', 'moderate') " | sed -n '2,$p' > proxy_list.txt 2>/dev/null

python proxy_verifier.py --gen > /dev/null 2>&1
python get_hidemyass.py > /dev/null 2>&1
python get_free_proxy_list.py > /dev/null 2>&1
python get_freeproxylists.py > /dev/null 2>&1

# verifier
python proxy_verifier.py --hidemyass  > /dev/null 2>&1  &
sleep 1
python proxy_verifier.py --free_proxy_list > /dev/null 2>&1 &
sleep 1
python proxy_verifier.py --freeproxylists  > /dev/null 2>&1 &
sleep 1

# verifier kxflag
python proxy_verifier.py --flag --hidemyass --kxflag good > /dev/null 2>&1 &
sleep 1
python proxy_verifier.py --flag --hidemyass --kxflag moderate > /dev/null 2>&1 &
sleep 1
python proxy_verifier.py --flag --free_proxy_list --kxflag good > /dev/null 2>&1 &
sleep 1
python proxy_verifier.py --flag --free_proxy_list --kxflag moderate > /dev/null 2>&1 &
sleep 1
python proxy_verifier.py --flag --freeproxylists --kxflag good > /dev/null 2>&1 &
sleep 1
python proxy_verifier.py --flag --freeproxylists --kxflag moderate > /dev/null 2>&1 &
