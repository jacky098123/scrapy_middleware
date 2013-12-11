mysql -h192.168.0.23 -uroot -pkooxoo crawlsystem -e "select concat('http://', ip, ':', cast(port as char)) from httpproxy" | sed -n '2,$p' > proxy_list.txt
