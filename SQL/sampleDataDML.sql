--initialize building with 8 rooms

insert into Building(num_rooms) values (8);


--initialize random equipment in rooms
insert into Equipment (name, room_num, maintenance_date) 
select 
    --generate a random equipment name
    case floor(random() * 8)
        when 0 then 'Treadmill'
        when 1 then 'Barbell'
        when 2 then 'Stationary Bike'
        when 3 then 'Dumbbells'
        when 4 then 'Elliptical Trainer'
        when 5 then 'Bench Press'
        when 6 then 'Rowing Machine'
        ELSE 'Leg Press Machine'
    end as name,
    --generate a random room number between 1 and 8
    floor(random() * 8) + 1 as room_num,
    --generate a random maintenance date between today and 35 days ago
    NOW() - (random() * (NOW()+'35 days' - NOW())) as maintenance_date
from generate_series(1, 100) as i;


--initialize employees
insert into Employee (first_name, last_name, is_trainer) values
('John', 'Doe', true),
('Alice', 'Smith', true),
('Michael', 'Johnson', true),
('Emma', 'Brown', true),
('Christopher', 'Davis', true),
('Olivia', 'Miller', true),
('James', 'Wilson', true),
('Sophia', 'Moore', true),
('William', 'Taylor', true),
('Isabella', 'Anderson', true),
('John', 'Doe', false),
('Alice', 'Smith', false),
('Michael', 'Johnson', false),
('Emma', 'Brown', false),
('Christopher', 'Davis', false),
('Olivia', 'Miller', false),
('James', 'Wilson', false),
('Sophia', 'Moore', false),
('William', 'Taylor', false),
('Isabella', 'Anderson', false);


--initialize club members
insert into Club_Member (username, join_date, membership_type, first_name, last_name) 
select
    -- random username
    'user' || floor(random() * 1000) as username,
    -- random join date between today and 90 days ago
    NOW() - (random() * (NOW()+'90 days' - NOW())) as join_date,
    case floor(random() * 2)
        when 0 then 'Basic'
        else 'Pro'
    end as membership_type,
    -- random first name
    case floor(random() * 10)
        when 0 then 'Alice'
        when 1 then 'Bob'
        when 2 then 'Charlie'
        when 3 then 'David'
        when 4 then 'Eve'
        when 5 then 'Frank'
        when 6 then 'Grace'
        when 7 then 'Heidi'
        when 8 then 'Ivan'
        when 9 then 'Judy'
        else 'Eve'
    end as first_name,
    -- random last name
    case floor(random() * 10)
        when 0 then 'Smith'
        when 1 then 'Johnson'
        when 2 then 'Brown'
        when 3 then 'Davis'
        when 4 then 'Miller'
        when 5 then 'Wilson'
        when 6 then 'Moore'
        when 7 then 'Taylor'
        when 8 then 'Anderson'
        when 9 then 'Thomas'
        else 'Wilson'
    end as last_name
    
from generate_series(1, 200) as i
on CONFLICT (username) DO NOTHING;

-- schedules for trainers
insert into Schedule (employee_id, schedule_start) 
select
    -- Select a random trainer_id from 1 to 5 (assuming there are 5 trainers)
    floor(random() * 5) + 1 as employee_id,
    -- Select a random timestamp from today to 90 days ahead between hours of 8:00 and 18:00
    NOW() + (random() * (NOW()+'90 days' - NOW())) as schedule_start
from generate_series(1, 500) as i
on conflict (employee_id, schedule_start) do nothing;




-- create classes
insert into Class(room_num, trainer_id, class_time, capacity, registered, exercise_type, price)
select
    floor(random() * 8) + 1 as room_num,
    -- Select trainer_id randomly from 1 to 5 (assuming there are 5 trainers)
    floor(random() * 5) + 1 as trainer_id,
    -- random timestamp in the past and future
    NOW() - (random() * (NOW()+'90 days' - NOW())) + (random() * '180 days'::interval) as class_time,

    floor(random() * 21) + 10 as capacity,
    0 as registered,
    -- Choose exercise type randomly
    CASE floor(random() * 8)
        when 0 then 'Cardio'
        when 1 then 'Strength'
        when 2 then 'HIIT'
        when 3 then 'Pilates'
        when 4 then 'Zumba'
        when 5 then 'Kickboxing'
        when 6 then 'Cycling'
        ELSE 'Yoga'
    end as exercise_type,
    -- Set price to a random number between 10 and 30
    CASE floor(random() * 3)
        when 0 then 25.00
        when 1 then 50.00
        ELSE 75.00
    end as price
from generate_series(1, 200) as i
where not exists -- no overlapping room_num, trainer_id, and class_time
(select * from Class c where c.trainer_id = trainer_id and c.class_time = class_time)
on conflict (room_num, class_time) do nothing;



-- add participants to classes 
DO $$
declare
    i integer;
    participants_count integer;
    chosen_class_id integer;
begin
    -- add participants to classes
    for i in 1..2000 loop
        select c.class_id into chosen_class_id
        from Class c
        where c.capacity > c.registered  -- respect capacity constraint
        order by random()
        limit 1;

        if chosen_class_id is not null then
            insert into Exercise (duration, exercise_date, exercise_type, class_id, username)
            select 
                60,
                c.class_time,
                c.exercise_type,
                c.class_id,
                (
                    select username 
                    from Club_Member
                    order by random() 
                    limit 1
                ) as username
            from Class c
            where c.class_id = chosen_class_id
           ON CONFLICT (username, exercise_date, class_id) DO NOTHING;

            -- update registered count
            update Class
            set registered = (
                select COUNT(*)
                from Exercise
                where Exercise.class_id = chosen_class_id  
            )
            where Class.class_id = chosen_class_id; 
        end if;
    end loop;
end $$;


-- book a bunch of solo training schedules based on trainer availability
DO $$
declare
    chosen_trainer_id integer;
    chosen_time timestamp;
    chosen_user varchar(255);
begin
    for i in 1..1000 loop
        select t.employee_id into chosen_trainer_id
        from Employee t
        where t.is_trainer = true
        order by random()
        limit 1;

        select s.schedule_start into chosen_time
        from Schedule s
        where s.employee_id = chosen_trainer_id
        order by random()
        limit 1;

        select u.username into chosen_user
        from Club_Member u
        where not exists (select e.exercise_date from Exercise e where e.username = u.username)
        order by random()
        limit 1;

        if chosen_trainer_id is not null and chosen_time is not null and chosen_user is not null then
            insert into Class (room_num, trainer_id, class_time, capacity, registered, exercise_type, price)
            select 
                -- Select room number randomly from 1 to 8
                floor(random() * 8) + 1 as room_num,
                chosen_trainer_id as trainer_id,
                chosen_time as class_time,
                1 as capacity,
                1 as registered, 
                'personal training' as exercise_type,
                50.00 as price
            -- update registered count
            where not exists -- no overlapping room_num, and class_time
            (select * from Class c where c.trainer_id = chosen_trainer_id and c.class_time = chosen_time)
            on conflict (room_num, class_time) DO NOTHING;

            insert into Exercise(duration, exercise_date, exercise_type, class_id, username)
            select 
                60,
                chosen_time,
                'personal training',
                (select c.class_id from Class c where c.trainer_id = chosen_trainer_id and c.class_time = chosen_time),
                chosen_user
            on conflict (class_id, username, exercise_date) DO NOTHING;

            delete from Schedule s
            where s.employee_id = chosen_trainer_id and s.schedule_start = chosen_time;

        end if;
    end loop;
end $$;


-- insert random exercise log data for all users
INSERT INTO Exercise(username, exercise_date, exercise_type, duration)
SELECT 
    Club_Member.username,
    DATE_TRUNC('minute', NOW() - (interval '1 day' * floor(random() * 30))),
    CASE (floor(random() * 8))
        WHEN 0 THEN 'Cardio'
        WHEN 1 THEN 'Strength'
        WHEN 2 THEN 'HIIT'
        WHEN 3 THEN 'Pilates'
        WHEN 4 THEN 'Zumba'
        WHEN 5 THEN 'Kickboxing'
        WHEN 6 THEN 'Cycling'
        ELSE 'Yoga'
    END as exercise_type,
    60
FROM 
    Club_Member
    CROSS JOIN generate_series(1, 15) as i
ON CONFLICT (username, exercise_date, class_id) DO NOTHING;


INSERT INTO Invoice (invoice_date, username, amount, paid)
SELECT 
-- random 1st of a month as date between 1 and 3 months ago

    date_trunc('month', NOW()) - (interval '1 month' * floor(random() * 3)) as invoice_date,
    club_member.username,
    club_member.monthly_fee as amount,
    -- randomly paid or not paid, unless the user is 'testuser' who is always unpaid
    CASE 
        WHEN club_member.username = 'testuser' THEN false
        ELSE random() < 0.67
    END as paid
FROM Club_Member;


-- insert unpaid invoices for classes that have not happened yet 
INSERT INTO Invoice (invoice_date, invoiced_service, username, amount, paid)
SELECT 
    class_time as invoice_date,
    class_id as invoiced_service,
    username,
    price as amount,
    false as paid
FROM (
    SELECT 
        c.class_time,
        c.price,
        e.class_id,
        e.username
    FROM Class c
    JOIN Exercise e ON c.class_id = e.class_id
) as class_participants
WHERE class_time > NOW() AND NOT EXISTS (
    SELECT * 
    FROM Invoice i
    WHERE i.username = class_participants.username
    AND i.invoice_date = class_participants.class_time
);


-- insert unpaid/paid invoices for classes that have already happened
INSERT INTO Invoice (invoice_date, invoiced_service, username, amount, paid)
SELECT 
    class_time as invoice_date,
    class_id as invoiced_service,
    username,
    price as amount,
    random() < 0.67 as paid
FROM (
    SELECT 
        c.class_time,
        c.price,
        e.class_id,
        e.username
    FROM Class c
    JOIN Exercise e ON c.class_id = e.class_id
) as class_participants
WHERE class_time <= NOW() AND NOT EXISTS (
    SELECT * 
    FROM Invoice i
    WHERE i.username = class_participants.username
    AND i.invoice_date = class_participants.class_time
);

-- insert health metric data
DO $$
begin 
    for i in 1..10000 loop
        insert into Health (username, date, weight, cardio_time, lifting_weight, weight_goal)
        select 
            username,
            DATE_TRUNC('second', NOW() - (interval '1 day' * floor(random() * 30))),
            floor(random() * 100) + 50 as weight,
            floor(random() * 60) as cardio_time,
            floor(random() * 100) as lifting_weight,
            floor(random() * 100) + 50 as weight_goal
        from (select username from Club_Member order by random() limit 25)
        on conflict (username, date) do nothing;
    end loop;
end $$;