CREATE TABLE orders (
    typeID bigint NOT NULL,
    regionID bigint NOT NULL,
    price double precision  NOT NULL,
    volRemaining bigint NOT NULL,
    orderRange bigint NOT NULL,
    orderID bigint NOT NULL,
    volEntered bigint NOT NULL,
    minVolume bigint NOT NULL,
    bid BOOLEAN NOT NULL,
    issueDate datetime NOT NULL,
    duration int NOT NULL,
    stationID bigint NOT NULL,
    solarSystemID bigint NOT NULL
);

CREATE TABLE history (
    typeID bigint NOT NULL,
    regionID bigint NOT NULL,
    issueDate datetime NOT NULL,
    orders bigint NOT NULL,
    low bigint NOT NULL,
    high bigint NOT NULL,
    average bigint NOT NULL,
    quantity bigint NOT NULL
);

CREATE TABLE systems (
    systemID bigint NOT NULL,
    systemName text NOT NULL,
    regionID bigint NOT NULL,
    faction bigint NOT NULL,
    security double precision NOT NULL,
    constellationID bigint NOT NULL,
    truesec double precision
);

CREATE TABLE stations (
    stationID bigint NOT NULL,
    stationName text NOT NULL,
    systemID bigint NOT NULL,
    corpid bigint NOT NULL
);

CREATE TABLE types (
    typeID bigint NOT NULL,
    typeName text NOT NULL,
    typeClass text,
    size double precision default 0.0 NOT NULL,
    published int,
    marketGroup int,
    groupID int,
    raceID int
);

CREATE TABLE regions (
    regionID bigint NOT NULL,
    regionName text NOT NULL
);
