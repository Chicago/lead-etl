

select address_id, bll, date from output.tests t where bll >= 8 and bll <=11 and address_id is not NULL and date > '2000-01-01';


select bll, count(distinct address_id) from output.tests group by 1;


select bll, count(distinct address_id) from (
select address_id, bll,date  from output.tests where bll >= 8 and bll <=11 and address_id is not NULL 
and date > '2000-01-01' and date < '2001-01-01'
) r
group by 1;



--need to verify that inspection was done for >=9 and not done for <9
-- possibly filter kids who moved to an address after getting exposed to lead somewhere else


select case when PreBLL <=9 then 'Control' else 'Treatment' end as PreBLL,avg(PostBLL) from 

(select address_id, max(bll) as PreBLL from output.tests where date > '2000-01-01' and date < '2001-01-01' 
group by 1 having max(bll)>=8 and max(bll) <= 11) a

inner join

(select address_id, max(bll) as PostBLL from  output.tests where date >= '2001-01-01'
group by 1) b

using (address_id)
group by 1;
  


