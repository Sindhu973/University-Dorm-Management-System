drop table if exists Applications cascade;
drop table if exists Payments cascade;
drop table if exists Orders cascade;
drop table if exists Cafes cascade;
drop table if exists Requests cascade;
drop table if exists Rooms_In cascade;
drop table if exists Buildings cascade;
drop table if exists Occupy cascade;
drop table if exists Students cascade;
drop table if exists Pay cascade;
drop table if exists Admins cascade;
drop table if exists Assigned_To cascade;
drop table if exists Employees cascade;
drop table if exists Items cascade;
drop table if exists Menus cascade;

create table Students (
sid integer primary key,
sfirst varchar(128) not null,
slast varchar(128) not null,
ph char(10),
email varchar(64),
address varchar(512),
dob varchar(16),
dept varchar(32),
program varchar(32)
);

create table Applications(
aid serial primary key,
sid integer not null,
pet varchar(3),
petPref varchar(3),
numFlat integer,
commPref char(1),
status varchar(16),
foreign key( sid ) references Students( sid )
);

create table Payments(
pid serial primary key,
term varchar(4),
amount decimal,
sid integer not null,
foreign key( sid ) references Students( sid )
);

create table Cafes(
cid integer primary key,
name varchar(128) not null,
timings varchar(32)
);

create table Items(
iid serial primary key,
iname varchar(32),
price decimal
);

create table Menus(
iid integer,
cid integer,
primary key( iid, cid ),
foreign key( iid ) references Items( iid ),
foreign key( cid ) references Cafes( cid )
);

create table Orders(
oid serial primary key,
quantity integer not null,
iid integer not null,
cost decimal,
sid integer not null,
cid integer not null,
foreign key( sid ) references Students( sid ),
foreign key( cid ) references Cafes( cid )
);

create table Requests(
rid serial primary key,
category varchar(32),
description varchar(128),
sid integer not null,
status varchar(16),
foreign key( sid ) references Students( sid )
);

create table Buildings (
bid integer primary key,
name varchar(64),
community char(1),
address varchar(128) not null
);

create table Rooms_In(
rid integer primary key,
tot_occupancy integer,
cur_occupancy integer,
pet_friendly varchar(3),
pet_exists varchar(3),
bid integer not null,
foreign key (bid) references Buildings( bid ) on delete cascade
);

create table Occupy(
sid integer,
rid integer,
bid integer,
primary key(sid, rid, bid ),
foreign key (sid) references Students( sid ),
foreign key (rid) references Rooms_In( rid ),
foreign key (bid) references Buildings( bid )
);

create table Employees(
eid integer primary key,
efirst varchar(128) not null,
elast varchar(128) not null,
dob varchar(16),
ph char(10),
email varchar(64),
address varchar(512),
category varchar(32)
);

create table Assigned_To(
eid integer,
rid integer,
primary key(eid,rid),
foreign key (eid) references Employees(eid),
foreign key (rid) references Requests(rid)
);

create table Admins (
adid integer primary key,
afirst varchar(128) not null,
alast varchar(128) not null,
dob varchar(16),
ph char(10),
address varchar(512),
email varchar(64)
);

create table Pay(
adid integer,
eid integer,
date varchar(16),
amount decimal,
primary key(adid,eid, date),
foreign key (adid) references Admins(adid),
foreign key (eid) references Employees(eid)
);

alter sequence applications_aid_seq restart with 100;
alter sequence requests_rid_seq restart with 100;
alter sequence payments_pid_seq restart with 100;