create table Trainer ( 
    employee_id serial primary key,
    first_name varchar(255)  not null,
    last_name varchar(255)  not null
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

CREATE TABLE Building (
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
    exercise_type varchar(255) not null,

    foreign key (trainer_id) references Trainer(employee_id),
    constraint unique_class UNIQUE (room_num, class_time)
);

create table Schedule (
    employee_id integer not null,
    schedule_start timestamp not null,
    schedule_end timestamp not null,

    primary key (employee_id, schedule_start),
    foreign key (employee_id) references Trainer(employee_id),
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
    exercise_type varchar(255) not null,
    class_id integer not null,
    username varchar(255) not null,
    foreign key (class_id) references Class(class_id),
    foreign key (username) references Club_Member(username),
    primary key (class_id, username)
);

CREATE OR REPLACE FUNCTION set_end_time()
RETURNS TRIGGER AS $$
BEGIN
    -- Set the end_time to be one hour after the start_time
    NEW.schedule_end := NEW.schedule_start + INTERVAL '1 hour';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER before_insert_update_schedule
BEFORE INSERT OR UPDATE ON Schedule
FOR EACH ROW
EXECUTE FUNCTION set_end_time();

CREATE OR REPLACE FUNCTION set_fee()
RETURNS TRIGGER AS $$
BEGIN
    -- Set the end_time to be one hour after the start_time
    NEW.monthly_free := CASE NEW.membership_type
        WHEN 'Basic' THEN 50.00
        ELSE 75.00
    END;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER before_insert_update_club_member
BEFORE INSERT OR UPDATE ON Club_Member
FOR EACH ROW
EXECUTE FUNCTION set_fee();




insert into Building(num_rooms) values (8);


INSERT INTO Equipment (name, room_num, maintenance_date) 
SELECT 
    --generate a random equipment name
    CASE floor(random() * 8)
        WHEN 0 THEN 'Treadmill'
        WHEN 1 THEN 'Barbell'
        WHEN 2 THEN 'Stationary Bike'
        WHEN 3 THEN 'Dumbbells'
        WHEN 4 THEN 'Elliptical Trainer'
        WHEN 5 THEN 'Bench Press'
        WHEN 6 THEN 'Rowing Machine'
        ELSE 'Leg Press Machine'
    END as name,
    --generate a random room number between 1 and 8
    floor(random() * 8) + 1 as room_num,
    --generate a random maintenance date between today and 90 days ahead
    NOW() + (random() * (NOW()+'90 days' - NOW())) as maintenance_date
FROM generate_series(1, 20) as i;


INSERT INTO Trainer (first_name, last_name) VALUES
('John', 'Doe'),
('Alice', 'Smith'),
('Michael', 'Johnson'),
('Emma', 'Brown'),
('Christopher', 'Davis');


INSERT INTO Club_Member (username, membership_type, first_name, last_name, user_weight, height, weight_goal) 
SELECT
    --generate a random username
    'user' || floor(random() * 1000) as username,
    --generate a random monthly fee of either 50 or 75
    CASE floor(random() * 2)
        WHEN 0 THEN 'Basic'
        ELSE 'Pro'
    END as membership_type,
    --generate a random first name
    CASE floor(random() * 10)
        WHEN 0 THEN 'Alice'
        WHEN 1 THEN 'Bob'
        WHEN 2 THEN 'Charlie'
        WHEN 3 THEN 'David'
        WHEN 4 THEN 'Eve'
        WHEN 5 THEN 'Frank'
        WHEN 6 THEN 'Grace'
        WHEN 7 THEN 'Heidi'
        WHEN 8 THEN 'Ivan'
        WHEN 9 THEN 'Judy'
        ELSE 'Eve'
    END as first_name,
    --generate a random last name
    CASE floor(random() * 10)
        WHEN 0 THEN 'Smith'
        WHEN 1 THEN 'Johnson'
        WHEN 2 THEN 'Brown'
        WHEN 3 THEN 'Davis'
        WHEN 4 THEN 'Miller'
        WHEN 5 THEN 'Wilson'
        WHEN 6 THEN 'Moore'
        WHEN 7 THEN 'Taylor'
        WHEN 8 THEN 'Anderson'
        WHEN 9 THEN 'Thomas'
        ELSE 'Wilson'
    END as last_name,
    --generate a random weight between 50 and 100
    floor(random() * 51) + 50 as user_weight,
    --generate a random height between 150 and 200
    floor(random() * 51) + 150 as height,
    --generate a random weight goal between 50 and 100
    floor(random() * 51) + 45 as weight_goal
FROM generate_series(1, 20) as i
ON CONFLICT (username) DO NOTHING;

INSERT INTO Schedule (employee_id, schedule_start) 
SELECT
    -- Select a random trainer_id from 1 to 5 (assuming there are 5 trainers)
    floor(random() * 5) + 1 as employee_id,
    -- Select a random timestamp from today to 90 days ahead between hours of 8:00 and 18:00
    NOW() + (random() * (NOW()+'90 days' - NOW())) as schedule_start
FROM generate_series(1, 20) as i;

INSERT INTO Class(room_num, trainer_id, class_time, capacity, exercise_type)
SELECT 
    -- Select room number randomly from 1 to 8
    floor(random() * 8) + 1 as room_num,
    -- Select trainer_id randomly from 1 to 5 (assuming there are 5 trainers)
    floor(random() * 5) + 1 as trainer_id,
    -- Select a random timestand from today to 90 days ahead
    NOW() + (random() * (NOW()+'90 days' - NOW())) + '30 days' as class_time,
    -- Set capacity to a random number between 10 and 30
    floor(random() * 21) + 10 as capacity,
    -- Choose exercise type randomly
    CASE floor(random() * 3)
        WHEN 0 THEN 'Cardio'
        WHEN 1 THEN 'Strength'
        ELSE 'Yoga'
    END as exercise_type
FROM generate_series(1, 20) as i
WHERE NOT EXISTS -- no overlapping room_num, trainer_id, and class_time
(SELECT * FROM Class c WHERE c.room_num = room_num AND c.trainer_id = trainer_id AND c.class_time = class_time)