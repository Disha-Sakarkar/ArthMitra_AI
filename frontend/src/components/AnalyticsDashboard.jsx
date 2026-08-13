import { useCallback, useEffect, useState } from "react";

const apiBaseUrl = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "");
const duration = (seconds = 0) => seconds >= 60 ? `${Math.floor(seconds / 60)}m ${Math.round(seconds % 60)}s` : `${Math.round(seconds)}s`;
const when = (value) => new Intl.DateTimeFormat("en-IN", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));

function MetricCard({ label, value, detail, tone = "stone" }) {
    const tones = { stone: "border-stone-200", green: "border-emerald-200 bg-emerald-50", red: "border-rose-200 bg-rose-50" };
    return <article className={`rounded-3xl border p-6 shadow-sm ${tones[tone]}`}><p className="text-xs font-bold uppercase tracking-wider text-stone-500">{label}</p><p className="mt-2 text-4xl font-bold text-emerald-950">{value}</p><p className="mt-2 text-sm text-stone-500">{detail}</p></article>;
}

export default function AnalyticsDashboard({ onBack }) {
    const [data, setData] = useState(null);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(true);
    const [updatedAt, setUpdatedAt] = useState(null);
    const load = useCallback(async () => {
        setLoading(true); setError("");
        try {
            const response = await fetch(`${apiBaseUrl}/api/call-analytics`);
            if (!response.ok) throw new Error();
            setData(await response.json()); setUpdatedAt(new Date());
        } catch { setError("Could not load analytics. Start the ArthMitra backend and try again."); }
        finally { setLoading(false); }
    }, []);
    useEffect(() => {
        load();
        const timer = window.setInterval(load, 15000);
        return () => window.clearInterval(timer);
    }, [load]);
    const total = data?.total_calls || 0;
    const success = data?.successful_calls || 0;
    const failed = data?.failed_calls || 0;
    const browser = data?.channels?.find((item) => item.channel === "browser");

    return <main className="min-h-screen bg-[#f8f4eb] px-4 py-8 text-[#18382e] sm:px-8"><div className="mx-auto max-w-6xl">
        <header className="mb-8 flex flex-col gap-4 md:flex-row md:items-start md:justify-between"><div><p className="text-sm font-semibold text-emerald-700">ArthMitra AI · Financial Services</p><h1 className="mt-1 text-4xl font-bold">Call Analytics</h1><p className="mt-3 max-w-3xl text-stone-600">Every browser call is recorded when it ends. A success means the caller received an eligibility answer or a scheme document list. This view contains aggregate, privacy-safe call data only.</p></div><button onClick={onBack} className="rounded-xl border border-emerald-900/20 px-4 py-2 text-sm font-semibold hover:bg-white">Back to calls</button></header>
        <div className="mb-8 flex items-center gap-3"><button onClick={load} disabled={loading} className="rounded-xl bg-[#1e513f] px-5 py-2.5 text-sm font-semibold text-white hover:bg-[#163e30] disabled:opacity-60">{loading ? "Refreshing…" : "Refresh now"}</button>{updatedAt && <span className="text-sm text-stone-500">Updated {updatedAt.toLocaleTimeString()}</span>}</div>
        {error ? <div className="rounded-2xl border border-rose-300 bg-rose-50 p-5 text-rose-700">{error}</div> : <>
            <section className="grid gap-5 md:grid-cols-3"><MetricCard label="Total calls · कुल कॉल" value={total} detail="All completed browser calls" /><MetricCard label="Successful · सफल" value={success} detail={`Success rate ${data?.success_rate || 0}%`} tone="green" /><MetricCard label="Failed · असफल" value={failed} detail="Did not reach the success condition" tone="red" /></section>
            <section className="mt-5 grid gap-5 md:grid-cols-2"><MetricCard label="Average duration" value={duration(data?.average_duration_seconds)} detail="Across all completed calls" /><MetricCard label="Success rate" value={`${data?.success_rate || 0}%`} detail={`${success} successful out of ${total} total calls`} /></section>
            <section className="mt-5 grid gap-5 lg:grid-cols-2"><article className="rounded-3xl border border-stone-200 bg-white p-6"><h2 className="text-lg font-bold">By channel · चैनल</h2><div className="mt-5 flex items-center gap-4"><span className="w-20 text-stone-600">Browser</span><div className="h-5 flex-1 overflow-hidden rounded-full bg-rose-300"><div className="h-full bg-emerald-700" style={{ width: `${browser?.total_calls ? (browser.successful_calls / browser.total_calls) * 100 : 0}%` }} /></div><span className="font-semibold">{browser?.successful_calls || 0} / {browser?.total_calls || 0}</span></div></article><article className="rounded-3xl border border-stone-200 bg-white p-6"><h2 className="text-lg font-bold">Why calls failed · असफल क्यों</h2><div className="mt-4 space-y-2 text-stone-600"><p className="flex justify-between"><span>No response</span><b>{data?.failure_reasons?.no_response || 0}</b></p><p className="flex justify-between"><span>Incomplete</span><b>{data?.failure_reasons?.incomplete || 0}</b></p></div></article></section>
            <section className="mt-5 overflow-hidden rounded-3xl border border-stone-200 bg-white"><div className="flex items-center justify-between p-6"><h2 className="text-lg font-bold">Recent calls · हाल की कॉलें</h2><span className="text-sm text-stone-500">Newest first</span></div><div className="overflow-x-auto"><table className="w-full min-w-[700px] text-left text-sm"><thead className="border-y border-stone-200 bg-stone-50 text-xs uppercase tracking-wider text-stone-500"><tr><th className="px-6 py-4">When</th><th>Channel</th><th>Duration</th><th>Outcome</th><th>Why</th></tr></thead><tbody>{data?.recent_calls?.length ? data.recent_calls.map((call, index) => <tr key={index} className="border-b border-stone-100"><td className="px-6 py-4">{when(call.started_at)}</td><td className="capitalize">{call.channel}</td><td>{duration(call.duration_seconds)}</td><td><span className={`rounded-full px-3 py-1 text-xs font-bold ${call.outcome === "successful" ? "bg-emerald-100 text-emerald-700" : "bg-rose-100 text-rose-700"}`}>{call.outcome === "successful" ? "Successful" : "Failed"}</span></td><td>{call.completion_kind === "document_list" ? "Document list provided" : call.completion_kind === "eligibility_check" ? "Eligibility answer provided" : call.failure_reason === "no_response" ? "No response" : "Incomplete"}</td></tr>) : <tr><td className="px-6 py-8 text-stone-500" colSpan="5">No completed calls yet. Make and end a browser call to see it here.</td></tr>}</tbody></table></div></section>
        </>}</div></main>;
}
