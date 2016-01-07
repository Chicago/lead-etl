drop table if exists aux.kid_edges;

create table aux.kid_edges as (

	select k1.id id1, k2.id id2, k1.initials
	from aux.kids_initial k1
	join aux.kids_initial k2
	on k2.initials = k1.initials
	and k2.id < k1.id
	and levenshtein_less_equal(k1.key, k2.key, 1) < 2

);

create index on aux.kid_edges (initials);