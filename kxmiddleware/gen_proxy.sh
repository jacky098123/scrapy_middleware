#mysql -h192.168.0.23 -uroot -pkooxoo crawlsystem -e "select concat('http://', ip, ':', cast(port as char)) from httpproxy" | sed -n '2,$p' > proxy_list.txt
mysql -h192.168.0.57 -uproduct_r -pproduct_r proxy -e "select concat('http://', ip, ':', cast(port as char)) from proxy_hidemyass where type = 'HTTP' and kxflag='good' and country='China' order by ip" | sed -n '2,$p' > proxy_list.txt
