export const API_BASE_URL = 'http://localhost:8000/api/';

export type Order = 'asc' | 'desc';

export interface WebsiteRecord {
    pk?: number,
    url: string,
    label: string,
    interval: number,
    active: boolean,
    regex: string,
    tags: string[]
}

export function createWebsiteRecord(
    url: string,
    label: string,
    interval: number,
    active: boolean,
    regex: string,
    tags: string[],
    pk?: number
): WebsiteRecord {
    return {
        pk,
        url,
        label,
        interval,
        active,
        regex,
        tags
    };
}

export function emptyWebsiteRecord(): WebsiteRecord {
    return {
        url: "",
        label: "",
        interval: 0,
        active: false,
        regex: "",
        tags: []
    };
}

export interface WebsiteRecordForView {
    pk: number,
    url: string,
    label: string,
    periodicity: string,
    active: boolean,
    tags: string[],
    last_crawl: string,
    lastExecutionStatus: string,
    actions: boolean
}

export function createWebsiteRecordForView(
    pk: number,
    url: string,
    label: string,
    periodicity: string,
    active: boolean,
    tags: string[],
    lastExecutionTime: string,
    lastExecutionStatus: string
): WebsiteRecordForView {
    return {
        pk,
        url,
        label,
        periodicity,
        active,
        tags,
        last_crawl: lastExecutionTime,
        lastExecutionStatus,
        actions: true
    };
}

export interface ExecutionRecord {
    pk: number,
    websiteRecordLabel: string,
    websiteRecordPk: number,
    status: string,
    lastExecutionTime: string,
    lastExecutionDuration: number,
    sitesCrawled: number
}

export function createExecutionRecord(
    pk: number,
    websiteRecordLabel: string,
    websiteRecordPk: number,
    status: string,
    lastExecutionTime: string,
    lastExecutionDuration: number,
    sitesCrawled: number
): ExecutionRecord {
    return {
        pk,
        websiteRecordLabel,
        websiteRecordPk,
        status,
        lastExecutionTime,
        lastExecutionDuration,
        sitesCrawled
    };
}

const periodicityRegex = /^((\d+)d)?((\d+)h)?((\d+)m)?$/g;

export function toPeriodicityString(period: number): string {
    let remaining = period;
    const days = (remaining / 1440) >> 0;
    remaining %= 1440;
    const hours = (remaining / 60) >> 0;
    const minutes = remaining % 60;
    return `${days}d ${hours}h ${minutes}m`;
};

export function fromPeriodicityString(periodicity: string): number | null {
    const match = periodicityRegex.exec(periodicity.replace(/\s/g, ''));
    if (match && (match[2] || match[4] || match[6])) {
        let period: number = 0;
        if (match[2]) {
            period += Number(match[2]) * 1440;
        }
        if (match[4]) {
            period += Number(match[4]) * 60;
        }
        if (match[6]) {
            period += Number(match[6]);
        }
        return period;
    }
    return null;
};