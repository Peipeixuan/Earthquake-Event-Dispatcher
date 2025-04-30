import React from "react";
import EventCard from "../components/event-card";
import Input from "../components/input";
import { useNavigate } from "react-router";
import "../styles/alert-report.css";  // ✅ 引入你新增的樣式

const mockData = {
  未接收: [
    { id: "10442-TP", eqTime: "2025/4/25, 17:20:34", alertTime: "2025/4/25, 17:21:34", magnitude: 3, level: "1" },
    { id: "10442-TP", eqTime: "2025/4/25, 17:20:34", alertTime: "2025/4/25, 17:21:34", magnitude: 3, level: "1" },
    { id: "10442-TP", eqTime: "2025/4/25, 17:20:34", alertTime: "2025/4/25, 17:21:34", magnitude: 3, level: "1" },
  ],
  待處理: [
    { id: "10442-TP", receiveTime: "2025/4/25, 17:20:34", alertSuccess: "否", deviceActivated: "否" },
    { id: "10442-TP", receiveTime: "2025/4/25, 17:20:34", alertSuccess: "否", deviceActivated: "否" },
  ],
  維修中: [
    { id: "10442-TP", receiveTime: "2025/4/25, 17:20:34", status: "未啟動" },
    { id: "10442-TP", receiveTime: "2025/4/25, 17:20:34", status: "未啟動" },
    { id: "10442-TP", receiveTime: "2025/4/25, 17:20:34", status: "未啟動" },
  ],
  已完成: [
    { id: "10442-TP", eqTime: "2025/4/25, 17:20:34", alertTime: "2025/4/25, 17:21:34", magnitude: 3, level: "1", finalLevel: "NA", receiveTime: "2025/4/25, 17:20:34", alertSuccess: "否", deviceActivated: "否", duration: "09:20:02" },
    { id: "10442-TP", eqTime: "2025/4/25, 17:20:34", alertTime: "2025/4/25, 17:21:34", magnitude: 3, level: "1", finalLevel: "NA", receiveTime: "2025/4/25, 17:20:34", alertSuccess: "否", deviceActivated: "否", duration: "09:20:02" },
  ]
};

export default function AlertReport() {
  const navigate = useNavigate();

  const sections = [
    { title: "未接收", color: "#E11D48" },
    { title: "待處理", color: "#F59E0B" },
    { title: "維修中", color: "#8B5CF6" },
    { title: "已完成", color: "#10B981" },
  ];

  return (
    <div className="min-h-screen bg-zinc-900 text-white p-6">
      <div
        onClick={() => navigate("/")}
        className="cursor-pointer text-sm text-white hover:underline mb-4"
      >
        &lt;&lt; Back To Dashboard
      </div>

      <h2 className="text-xl font-bold mb-4">Alert Report</h2>

      <div className="mb-6">
        <Input title="廠區">
          <select className="bg-transparent text-white border-none focus:ring-0">
            <option value="Taipei">Taipei</option>
          </select>
        </Input>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {sections.map(({ title, color }) => (
          <div key={title} className="rounded overflow-hidden flex flex-col bg-[#1A1B1F]">
            <div className="h-1" style={{ backgroundColor: color }}></div>
            <div className="p-4 font-semibold">{title}</div>
            <div className="overflow-y-auto flex-1 px-4 pb-4 space-y-4 custom-scrollbar"
                 style={{ maxHeight: "calc(100vh - 240px)" }}>
              {(mockData[title] || []).map((data, i) => (
                <EventCard key={i} status={title} data={data} />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
