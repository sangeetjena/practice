CREATE TABLE users (
    tenant_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    name TEXT NOT NULL,
    PRIMARY KEY (tenant_id, user_id)
);

SELECT create_distributed_table('users', 'tenant_id');

INSERT INTO users (tenant_id, user_id, name)
VALUES (1001, 1, 'example');

SELECT * FROM users WHERE tenant_id = 1001;