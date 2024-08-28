create database redbus;

create table bus_routes(
id 	int AUTO_INCREMENT,
route_name text,
route_link	text,
busname 	text,
bustype	text,
departing_time time,
star_rating	float,
price 	decimal (10,0),
seats_available	int,
state text,
operator text

)
