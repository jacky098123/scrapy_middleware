DB_CONF = {
    "host"  : "60.28.205.233",
    "user"  : "proxy_w",
    "passwd": "proxy@KX0528",
    "database"  : "proxy",
    "port"      : 3306,
    "charset"   : "utf8"
}




'''
drop table if exists proxy_hidemyass;
create table proxy_hidemyass (
id int auto_increment,
ip varchar(64) default '',
port varchar(16) default '',
country varchar(64) default '',
type varchar(16) default '',
anonymity varchar(32) default '',
kxflag varchar(16) default '' comment 'good,moderate,pool,bad',
create_time timestamp default '0000-00-00 00:00:00',
update_time timestamp default CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
primary key(id),
key idx_u(ip, port)
) engine=InnoDb, charset='utf8';

drop table if exists proxy_free_proxy_list;
create table proxy_free_proxy_list (
id int auto_increment,
ip varchar(64) default '',
port varchar(16) default '',
code varchar(16) default '',
country varchar(32) default '',
anonymity varchar(32) default '',
google varchar(16) default '',
https varchar(16) default '',
kxflag varchar(16) default '',
create_time timestamp default '0000-00-00 00:00:00',
update_time timestamp default current_timestamp on update current_timestamp,
primary key(id),
key idx_u(ip, port)
) engine=InnoDb, charset='utf8';

drop table if exists proxy_freeproxylists;
create table proxy_freeproxylists (
id int auto_increment,
ip varchar(64) default '',
port varchar(32) default '',
protocol varchar(16) default '',
anonymity varchar(16) default '',
country varchar(32) default '',
region varchar(32) default '',
city varchar(32) default '',
kxflag varchar(16) default '',
create_time timestamp default '0000-00-00 00:00:00',
update_time timestamp default current_timestamp on update current_timestamp,
primary key(id),
key idx_u(ip, port)
)engine=InnoDb, charset='utf8';

'''
