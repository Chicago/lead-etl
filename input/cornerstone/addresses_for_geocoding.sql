\COPY (select addr_ln1_t,addr_zip_n,addr_cty_t, array_agg(ogc_fid) from cornerstone.partaddr group by 1,2,3) to STDOUT with csv header;
