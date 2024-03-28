create table Employee ( 
    employee_id serial primary key,
    first_name varchar(255)  not null,
    last_name varchar(255)  not null,
    is_trainer boolean not null
);

create table Club_Member ( 
    username varchar(255) not null primary key,
    monthly_free float not null,
    membership_type varchar(255) not null,
    first_name varchar(255) not null,
    last_name varchar(255) not null,
    user_weight float not null,
    height float not null,
    weight_goal float not null
);

create table Building (
    id SERIAL PRIMARY KEY,
    num_rooms integer not null
);

create table Equipment (
    equipment_id serial primary key,
    name varchar(255) not null,
    room_num integer,
    maintenance_date date
);

create table Class (
    class_id serial primary key,
    room_num integer not null,
    trainer_id integer not null,
    class_time timestamp not null,
    capacity integer not null,
    registered integer not null,
    exercise_type varchar(255) not null,

    foreign key (trainer_id) references Employee(employee_id),
    constraint unique_class UNIQUE (room_num, class_time),
    constraint class_capacity_constraint CHECK (registered <= capacity)
);

create table Schedule (
    employee_id integer not null,
    schedule_start timestamp not null,
    schedule_end timestamp not null,

    primary key (employee_id, schedule_start),
    foreign key (employee_id) references Employee(employee_id),
    constraint schedule_hour_constraint CHECK (schedule_end = schedule_start + INTERVAL '1 hour')
);

create table Invoice (
    invoice_id serial primary key,
    invoice_date date not null,
    username varchar(255) not null,
    amount float not null,
    invoiced_service varchar(255) not null,
    paid boolean not null,
    foreign key (username) references Club_Member(username)
);

create table Exercise (
    duration float not null,
    exercise_date date not null,
    exercise_type varchar(255) not null,
    class_id integer not null,
    username varchar(255) not null,
    foreign key (class_id) references Class(class_id),
    foreign key (username) references Club_Member(username),
    primary key (class_id, username)
);
