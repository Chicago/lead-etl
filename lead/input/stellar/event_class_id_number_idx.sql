drop index if exists event_class_id_number_idx;
create index on stellar.event (class, id_number);
