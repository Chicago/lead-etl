drop table if exists output.investigations;

create table output.investigations as (
with investigations as (
select
    address_id, apt,
    ins_ref_dt as referral_date,
    insp_comp as init_date,
    insrslsum in ('I', 'B') as hazard_int,
    insrslsum in ('E', 'B') as hazard_ext,

    abt_cmp_dt as abatement_date,
    addr_cl_dt as closure_date,
    adr_cl_rsn as closure_reason,
    CASE 
        WHEN adr_cl_rsn ~* '(NOH|NO H|COMPO|NEG|ALL|HUD|CMPL)' THEN 1
        WHEN upper(adr_cl_rsn) in (
            'CMPLY','COMPLIED','COMPLY','OCMPLY',',COMPLY','CMPY',
            'COMPONENTS','COMPONENTS ACCE','COMPONENTS ACCP','COMP  ACCEPT',
            'COMPONENTS ACC','COMPENTS','ACCECPTABLE', 'ALLCOMPONENTS A',
            'COMP  ACCEPT','COMPOMENTS ACCE','COMPONENTES ACC',
            'COMPONENTS ACC', 'COMPONENTS ACCE','COMPONETS ACCP',
            'COMPTS ACCEPTAB',
            'COMPONENTS ACCP','COMPONETS ACCEP','COMPONETSACCEPT','CONPONENTS ACC',
            'ACCEPTABLE','CIOMPLIED','CIOMPLY','CMPY','CMPLY', 'ALL COMP. ACCEP',
            'ALL COMP ACCEPT',
            'CMPLY/BGT','COMP. ACCEPT','COMP ACCEPTABLE', 'COMPLYED', 'COMPLY`', 
            'COMPOMENT ACCE',  'COMPONMENT ACCE', 'COMPY',
            'ACOMPONENTS ACC','WORK COMPLETE','COMP ACCEPT',
            'NO HAZARD',   'NO HAZARDS', 'NO  HAZARDS','NO CAUSE',
            ',NO HAZARDS','NO  HAZARDS','NO HAZARTS',
            ',NO HAZARDS',',NO H AZARDS','N-HAZ/COMP-ACC','N O HAZARDS',',NO HAZRDS',
            'NOHAZARDS',
            'NO HARZARDS','NO HAZZARDS','N-HAZ', 'NO HAZZARD','NO HARZARD') THEN 1
        WHEN adr_cl_rsn ~* 'ADM' THEN 2
        WHEN adr_cl_rsn ~* 'DEL' THEN 3
        WHEN adr_cl_rsn ~* 'COURT' THEN 4
        WHEN adr_cl_rsn ~* 'MOVE' THEN 5
        WHEN adr_cl_rsn ~* 'REFU' THEN 6
        WHEN adr_cl_rsn ~* 'LOC' THEN 7
        WHEN adr_cl_rsn ~* 'VAC' THEN 8
        WHEN adr_cl_rsn ~* 'WRO' THEN 9
        WHEN adr_cl_rsn ~* 'DUP' THEN 10
        WHEN adr_cl_rsn ~* 'RAZ' THEN 11
        WHEN adr_cl_rsn ~* 'SATTY' THEN 12
    END as closure_code

from stellar.invest 
join aux.stellar_addresses using (addr_id)
)

select *, 
    CASE WHEN abatement_date is not null THEN abatement_date
    WHEN closure_code = 1 THEN closure_date END as comply_date
FROM investigations
);

