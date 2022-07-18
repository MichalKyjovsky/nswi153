import axios from 'axios';
import { AxiosInstance } from 'axios';
import {
    WebsiteRecordForView,
    createWebsiteRecordForView,
    toPeriodicityString,
    WebsiteRecord,
    createWebsiteRecord,
    ExecutionRecord,
    createExecutionRecord,
    API_BASE_URL,
    Order,
    createLayoutEdge,
    createLayoutGraph,
    createLayoutNode,
    LayoutGraph,
    LayoutNode
} from './Common';

interface ResponseExecutionPage {
    pk: number,
    fields: {
        title: string,
        url: string,
        crawl_duration: number,
        last_crawl: string,
        website_record: number,
        status: string,
        label: string
    },
    links: number
}

interface ResponseData {
    executions: ResponseExecutionPage[],
    total_pages: number,
    total_records: number
}

interface ExecutionsResponse {
    executions: ExecutionRecord[],
    totalPages: number,
    totalRecords: number
}

interface RecordsListResponse {
    records: WebsiteRecordForSelect[]
}

export interface WebsiteRecordForSelect {
    pk: number,
    label: string
}

interface ResponseRecordPage {
    pk: number,
    fields: {
        url: string,
        label: string,
        interval: number,
        active: boolean,
        regex: string
    },
    tags: string[],
    last_crawl: string,
    last_status: string
}

interface ResponseData {
    records: ResponseRecordPage[],
    total_pages: number,
    total_records: number
}

interface ResponseRecord {
    pk: number,
    fields: {
        url: string,
        label: string,
        interval: number,
        status: number,
        regex: string,
        tags: string[]
    }
}

interface WebsiteResponse {
    records: WebsiteRecordForView[],
    totalPages: number,
    totalRecords: number
}

interface GraphResponseNode {
    pk: number,
    fields: {
        crawl_time: string,
        url: string,
        owner: number
    }
}

interface GraphResponseEdge {
    model: string,
    pk: number,
    fields: {
        source: number,
        target: number
    }
}

interface GraphResponse {
    nodes: GraphResponseNode[],
    edges: GraphResponseEdge[]
}

export default class ApiManager {
    inst: AxiosInstance;

    constructor() {
        this.inst = axios.create({
            baseURL: API_BASE_URL,
            timeout: 1000,
        });
    }

    async getExecutionPage(pageSize: number, pageNumber: number, websiteFilter?: number): Promise<ExecutionsResponse | null> {
        try {
            const path = `execution${websiteFilter ? `/${websiteFilter}/` : "s/"}${pageNumber + 1}/`;
            const response = await this.inst.get(path, {
                params: {
                    page_size: pageSize
                }
            });
            const data: ResponseData = response.data;
            return {
                executions: data.executions.map(rec => createExecutionRecord(rec.pk, rec.fields.label, rec.fields.website_record, rec.fields.status, rec.fields.last_crawl, rec.fields.crawl_duration, rec.links)),
                totalPages: data.total_pages,
                totalRecords: data.total_records
            };
        } catch (error) {
            console.error(error);
        }
        return null;
    }

    async listRecords(): Promise<WebsiteRecordForSelect[] | null> {
        try {
            const path = 'record/list/';
            const response = await this.inst.get(path);
            const data: RecordsListResponse = response.data;
            return data.records;
        } catch (error) {
            console.error(error);
        }
        return null;
    }

    async getRecordPage(pageSize: number, pageNumber: number, labelFilter: string, tagsFilter: string, urlFilter: string, order: Order, orderBy: keyof WebsiteRecordForView): Promise<WebsiteResponse | null> {
        try {
            const response = await this.inst.get(`record/${pageNumber + 1}/`, {
                params: {
                    page_size: pageSize,
                    "label-filter": labelFilter.trim().length > 0 ? labelFilter.trim() : undefined,
                    "url-filter": urlFilter.trim().length > 0 ? urlFilter.trim() : undefined,
                    "tag-filter": tagsFilter.trim().length > 0 ? tagsFilter.trim() : undefined,
                    sort_property: orderBy,
                    sort_order: order.toUpperCase()
                }
            });
            const data: ResponseData = response.data;
            return {
                records: data.records.map(rec => createWebsiteRecordForView(rec.pk, rec.fields.url, rec.fields.label, toPeriodicityString(rec.fields.interval), rec.fields.active, rec.tags, rec.last_crawl, rec.last_status)),
                totalPages: data.total_pages,
                totalRecords: data.total_records
            };
        } catch (error) {
            console.error(error);
        }
        return null;
    }

    async getRecord(id: number): Promise<WebsiteRecord | null> {
        try {
            const response = await this.inst.get("record/", {
                params: {
                    record: id
                }
            });
            const data: ResponseRecord[] = response.data;
            const transformed = data.map(rec => createWebsiteRecord(rec.fields.url, rec.fields.label, rec.fields.interval, rec.fields.status === 1 ? true : false, rec.fields.regex, rec.fields.tags, rec.pk));
            return transformed.length > 0 ? transformed[0] : null;
        } catch (error) {
            console.error(error);
        }
        return null;
    }

    async deleteRecord(id: number) {
        try {
            const response = await this.inst.delete("record/", {
                data: {
                    record_id: id
                }
            });
            if (response.status !== 200) {
                return false;
            }
            return true;
        } catch (error) {
            console.log(error);
            return false;
        }
    }

    async executeRecord(id: number) {
        try {
            const response = await this.inst.post(`execution/${id}/`);
            if (response.status > 200) {
                return false;
            }
            return true;
        } catch (error) {
            console.log(error);
            return false;
        }
    }

    async getGraph(records: string): Promise<LayoutGraph | null> {
        try {
            const response = await this.inst.get("graph/", {
                params: {
                    records
                }
            });
            const data: GraphResponse = response.data;

            const nodes = data.nodes
                .map(node => createLayoutNode(node.pk.toString(), node.fields.crawl_time, node.fields.url, node.fields.owner));

            const nodesMap: Record<string, LayoutNode> = {};
            nodes.forEach(node => nodesMap[node.id] = node);

            const edges = data.edges
                .map(edge => createLayoutEdge(nodesMap[edge.fields.source.toString()], nodesMap[edge.fields.target.toString()]));

            return createLayoutGraph(nodes, edges);
        } catch (error) {
            console.log(error);
        }
        return null;
    }
}