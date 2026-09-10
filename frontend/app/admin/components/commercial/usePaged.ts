"use client";
import { useCallback, useEffect, useState } from "react";
import api from "../../../lib/api";
import { errorText, PageData, Row } from "./common";
export function usePaged(path: string, filters: Record<string, unknown> = {}) {
  const [data, setData] = useState<PageData>({ items: [], total: 0, page: 1, page_size: 20 });
  const [loading, setLoading] = useState(false); const [error, setError] = useState<string>();
  const load = useCallback(async (page = data.page, pageSize = data.page_size) => {
    setLoading(true); setError(undefined);
    try { const response = await api.get<PageData>(path, { params: { ...filters, page, page_size: pageSize } }); setData(response.data); }
    catch (e) { setError(errorText(e)); } finally { setLoading(false); }
  }, [path, JSON.stringify(filters), data.page, data.page_size]); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { void load(1, data.page_size); }, [path, JSON.stringify(filters)]); // eslint-disable-line react-hooks/exhaustive-deps
  return { ...data, rows: data.items as Row[], loading, error, load };
}
