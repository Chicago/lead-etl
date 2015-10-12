DROP TABLE IF EXISTS aux.wic_addresses;

CREATE TABLE aux.wic_addresses AS (
    select wk.kid_id, a.id address_id from wic.wic_infant w join wic.wic_kids wk on w.id = wk.wic_id join wic.wic_addresses using (addr_ln1_t, addr_zi) join aux.addresses a using (address)
);
