create table Employee ( 
    employee_id serial primary key,
    first_name varchar(255)  not null,
    last_name varchar(255)  not null,
    is_trainer boolean not null
);

create table Club_Member ( 
    username varchar(255) not null primary key,
    join_date date not null,
    monthly_fee float not null,
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
    price float not null,

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
    invoiced_service integer,
    paid boolean not null,
    foreign key (username) references Club_Member(username)
    foreign key (invoiced_service) references Class(class_id)
);

create table Exercise (
    duration float not null,
    exercise_date timestamp not null,
    exercise_type varchar(255) not null,
    class_id integer not null,
    username varchar(255) not null,
    foreign key (class_id) references Class(class_id),
    foreign key (username) references Club_Member(username),
    primary key (class_id, username)
);

create table Health (
    username varchar(255) not null,
    date timestamp not null,
    weight float not null,
    cardio_time float not null,
    lifting_weight float not null,
    weight_goal float not null,
    primary key (username, date),
    foreign key (username) references Club_Member(username)
);


-- this trigger ensures that schedules are always on the hour, and end time is exactly one hour after start time
create or replace function set_end_time()
returns TRIGGER as $$
begin
    NEW.schedule_start = DATE_TRUNC('hour', NEW.schedule_start) + INTERVAL '0 minutes' + INTERVAL '0 seconds' ;
        -- Set the end_time to be one hour after the start_time
    NEW.schedule_end := NEW.schedule_start + INTERVAL '1 hour';
    return NEW;
end;
$$ language plpgsql;

create trigger before_insert_update_schedule
before insert or update on Schedule
for EACH row
execute function set_end_time();

-- this trigger ensures that the monthly fee is set based on the membership type
create or replace function set_fee()
returns TRIGGER as $$
begin
    -- 
    NEW.monthly_fee := case NEW.membership_type
        when 'Basic' then 50.00
        else 75.00
    end;
    return NEW;
    INSERT INTO Invoice (invoice_date, username, amount, invoiced_service, paid)
    VALUES 
        (NEW.join_date, NEW.username, NEW.monthly_fee, 'Membership Fee', false);
end;
$$ language plpgsql;

create trigger before_insert_club_member
before insert or update on Club_Member
for EACH row
execute function set_fee();


-- this trigger ensures that schedules are always on the hour, and end time is exactly one hour after start time
create or replace function set_class_time()
returns TRIGGER as $$
begin
    NEW.class_time = DATE_TRUNC('hour', NEW.class_time) + INTERVAL '0 minutes' + INTERVAL '0 seconds' ;
    return NEW;
end;
$$ language plpgsql;

create trigger before_insert_update_class
before insert or update on Class
for EACH row
execute function set_class_time();