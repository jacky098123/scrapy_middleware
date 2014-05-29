#cur_dir=$(cd "$(dirname "$0")"; pwd)
cd "$(dirname "$0")"

export PATH=/usr/local/bin:$PATH

#python proxy_verifier.py --gen > /dev/null 2>&1
python get_hidemyass.py > /dev/null 2>&1
python get_free_proxy_list.py > /dev/null 2>&1
python get_freeproxylists.py > /dev/null 2>&1

# verifier
python proxy_verifier.py --hidemyass  > /dev/null 2>&1  &
python proxy_verifier.py --free_proxy_list > /dev/null 2>&1 &
python proxy_verifier.py --freeproxylists  > /dev/null 2>&1 &

# verifier kxflag
python proxy_verifier.py --hidemyass --flag good > /dev/null 2>&1  &
python proxy_verifier.py --hidemyass --flag moderate > /dev/null 2>&1  &
python proxy_verifier.py --free_proxy_list --flag good > /dev/null 2>&1  &
python proxy_verifier.py --free_proxy_list --flag moderate > /dev/null 2>&1  &
python proxy_verifier.py --freeproxylists --flag good > /dev/null 2>&1  &
python proxy_verifier.py --freeproxylists --flag moderate > /dev/null 2>&1  &
