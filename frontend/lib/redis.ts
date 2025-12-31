import Redis from 'ioredis';

const getRedisUrl = () => {
    if (process.env.UPSTASH_REDIS_URL) {
        return process.env.UPSTASH_REDIS_URL;
    }
    throw new Error("UPSTASH_REDIS_URL is not defined");
};

export const redis = new Redis(getRedisUrl());
