import React from "react";
import Input from "../components/input";
import { useNavigate } from "react-router";
import "../styles/alert-report.css";
import axiosInstance from "../axiosInstance";
import { API_UNACKNOWLEDGED, API_ACKNOWLEDGE, API_PENDING, API_SUBMIT, API_IN_PROGRESS, API_REPAIR, API_CLOSED} from "../globals/constants";
import { useEffect, useState } from "react";


export default function AlertReport() {
  const navigate = useNavigate();

  const [selectedRegion, setSelectedRegion] = useState("Taipei");
  const [unacknowledgedData, setUnacknowledgedData] = useState([]);
  const [pendingData, setPendingData] = useState([]);
  const [inProgressData, setInProgressData] = useState([]);
  const [closedData, setClosedData] = useState([]);


  useEffect(() => {
    fetchUnacknowledged();
    fetchPendingEvents();
    fetchInProgressEvents();
    fetchClosedEvents();
  }, []);

  const fetchUnacknowledged = async (region = selectedRegion) => {
    console.log("送出的地區參數：", region);
    try {
      const response = await axiosInstance.get(API_UNACKNOWLEDGED, {params: { location: region }});

      console.log("後端回傳資料：", response.data);

      // 格式化資料
      const formatted = response.data.map((item) => ({
        ...item,
        earthquake_time: new Date(item.earthquake_time).toLocaleString("zh-TW"),
        alert_time: new Date(item.alert_time).toLocaleString("zh-TW"),
        magnitude: parseFloat(item.magnitude).toFixed(1),
        intensity: `${parseFloat(item.intensity).toFixed(1)} 級`,
        level: item.level === 1 ? "L1" : item.level === 2 ? "L2" : "NA"
      }));

      setUnacknowledgedData(formatted);
    } catch (error) {
      console.error("Failed to fetch unacknowledged events:", error);
    }
  };

  const handleAcknowledge = async (eventId) => {
    try {
      const response = await axiosInstance.post(API_ACKNOWLEDGE, { event_id: eventId });
      console.log("已接收事件:", response.data);
      alert(`✅ 已成功接收事件 ${eventId}`);

      // 及時更新未接收與待處理
      fetchUnacknowledged(selectedRegion);
      fetchPendingEvents(selectedRegion);
    } catch (error) {
      console.error("接收事件失敗:", error);
      alert("接收事件失敗！");
    }
  };

  const fetchPendingEvents = async (region = selectedRegion) => {
    try {
      const response = await axiosInstance.get(API_PENDING,  {params: { location: region }});
      console.log("待處理事件：", response.data);

      // 格式化資料（根據你的欄位結構調整）
      const formatted = response.data.map((item) => ({
        ...item,
        ackTime: new Date(item.ack_time).toLocaleString("zh-TW"),
      }));

      setPendingData(formatted);
    } catch (error) {
      console.error("Failed to fetch pending events:", error);
    }
  };

  const handleSubmitEvent = async (eventId, if_damage, if_operation_active) => {
    const payload = {
        event_id: eventId,
        damage: if_damage,
        operation_active: if_operation_active
    };

    console.log("送出的 submit payload：", payload);

    try {
      const response = await axiosInstance.post(API_SUBMIT, payload);
      console.log("事件已送出:", response.data);
      alert(`事件 ${eventId} 已成功送出！`);

      // 即時更新待處理與維修中
      fetchPendingEvents(selectedRegion);
      fetchInProgressEvents(selectedRegion);
    } catch (error) {
      console.error("事件送出失敗:", error);
      alert("事件送出失敗！");
    }
  };

  const fetchInProgressEvents = async (region = selectedRegion) => {
    try {
      const response = await axiosInstance.get(API_IN_PROGRESS, {
        params: { location: region },
      });

      console.log("維修中事件：", response.data);

      const formatted = response.data.map((item) => ({
        ...item,
        ackTime: new Date(item.ack_time).toLocaleString("zh-TW"),
        operationActivated: item.is_operation_active === 1 ? "已啟動" : "未啟動",
      }));

      setInProgressData(formatted);
    } catch (error) {
      console.error("Failed to fetch in-progress events:", error);
    }
  };

  const handleRepairConfirm = async (eventId) => {
    try {
      const response = await axiosInstance.post(API_REPAIR, {event_id: eventId});
      console.log("已確認修復完成:", response.data);
      alert(`✅ 事件 ${eventId} 修復已確認`);

      // 即時更新維修中與已完成
      fetchInProgressEvents(selectedRegion);
      fetchClosedEvents(selectedRegion);
    } catch (error) {
      console.error("修復確認失敗:", error);
      alert("修復確認失敗！");
    }
  };

  const fetchClosedEvents = async (region = selectedRegion) => {
    try {
      const response = await axiosInstance.get(API_CLOSED, {
        params: { location: region }
      });
      console.log("已完成事件：", response.data);

      const formatted = response.data.map((item) => ({
        ...item,
        earthquakeTime: new Date(item.earthquake_time).toLocaleString("zh-TW"),
        alertTime: new Date(item.alert_time).toLocaleString("zh-TW"),
        ackTime: new Date(item.ack_time).toLocaleString("zh-TW"),
        operationActivated: item.is_operation_active === 1 ? "已啟動" : "未啟動",
        isDamage: item.is_damage === 1 ? "是" : "否",
      }));

      setClosedData(formatted);
    } catch (error) {
      console.error("Failed to fetch closed events:", error);
    }
  };

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
          <select
            className="bg-transparent text-white border-none focus:ring-0"
            value={selectedRegion}
            onChange={(e) => {
              const newRegion = e.target.value;
              setSelectedRegion(newRegion);
              fetchUnacknowledged(newRegion);
              fetchPendingEvents(newRegion);
              fetchInProgressEvents(newRegion);
              fetchClosedEvents(newRegion);
            }}
          >
            <option value="Taipei">台北</option>
            <option value="Hsinchu">新竹</option>
            <option value="Taichung">台中</option>
            <option value="Tainan">台南</option>
            <option value="all">全部</option>
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
              {(
                title === "未接收" ? unacknowledgedData :
                title === "待處理" ? pendingData :
                title === "維修中" ? inProgressData :
                title === "已完成" ? closedData :
                mockData[title] || []
              ).map((data, i) => (
                <EventCard
                  key={i}
                  status={title}
                  data={data}
                  onAcknowledge={title === "未接收" ? handleAcknowledge : undefined}
                  onSubmit={title === "待處理" ? handleSubmitEvent : undefined}
                  onRepairConfirm={title === "維修中" ? handleRepairConfirm : undefined}
                />
              ))}              
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function EventCard({ status, data, onAcknowledge, onSubmit,onRepairConfirm }) {
  const actionMap = {
    未接收: "接收",
    待處理: "送出",
    維修中: "確認修復完成",
  };

  const buttonColorMap = {
    未接收: "bg-pink-600 hover:bg-pink-700",
    待處理: "bg-amber-500 hover:bg-amber-600",
    維修中: "bg-purple-500 hover:bg-purple-600",
  };

  const [damage, setDamage] = useState(null);
  const [operationActive, setOperationActive] = useState(null);

  const handleClick = () => {
    if (status === "未接收" && onAcknowledge) {
      onAcknowledge(data.event_id);
    }

    if (status === "待處理" && onSubmit) {
      if (damage === null || operationActive === null) {
        alert("請選擇是否造成損傷與是否啟動戰情");
        return;
      }
      
      onSubmit(data.event_id, damage, operationActive);
    }

    if (status === "維修中" && onRepairConfirm) {
      onRepairConfirm(data.event_id);
    }
  };

  return (
    <div className="bg-[#22252C] text-white rounded shadow-sm overflow-hidden">
      <div className="bg-[#23252A] border-b border-black px-4 py-2 font-semibold">
        Event ID {data.event_id}
      </div>

      <div className="px-4 py-4 text-sm space-y-1">
        {status === "未接收" && (
          <>
            <div>地震時間：{data.earthquake_time}</div>
            <div>警報時間：{data.alert_time}</div>
            <div>芮氏規模：{data.magnitude}</div>
            <div>廠區震度：{data.intensity}</div>
            <div>嚴重程度：{data.level}</div>
          </>
        )}

        {status === "待處理" && (
          <>
            <div>接收時間：{data.ackTime}</div>
            <div>
              是否造成損傷?：
              <label className="ml-2">
                <input type="radio" className="accent-amber-500" name={`damage-${data.event_id}`} checked={damage === true} onChange={() => setDamage(true)} /> 是         
              </label>
              <label className="ml-2">
                <input type="radio" className="accent-amber-500" name={`damage-${data.event_id}`} checked={damage === false} onChange={() => setDamage(false)} /> 否
              </label>
            </div>
            <div>
              是否啟動戰情?：
              <label className="ml-2">
                <input type="radio" className="accent-amber-500" name={`activate-${data.event_id}`} checked={operationActive === true} onChange={() => setOperationActive(true)} /> 是
              </label>
              <label className="ml-2">
                <input type="radio" className="accent-amber-500" name={`activate-${data.event_id}`} checked={operationActive === false} onChange={() => setOperationActive(false)}/> 否
              </label>
            </div>
            <div>
              <a href="#" className="text-cyan-400 text-sm">更多事件資訊</a>
            </div>
          </>
        )}

        {status === "維修中" && (
          <>
            <div>接收時間：{data.ackTime}</div>
            <div>戰情啟動狀態：{data.operationActivated}</div>
            <div>
              <a href="#" className="text-cyan-400 text-sm">更多事件資訊</a>
            </div>
          </>
        )}

        {status === "已完成" && (
          <>
            <div>地震時間：{data.earthquakeTime}</div>
            <div>警報時間：{data.alertTime}</div>
            <div>芮氏規模：{data.magnitude}</div>
            <div>廠區震度：{data.intensity}</div>
            <div>嚴重程度：{data.level}</div>
            <div>接收時間：{data.ackTime}</div>
            <div>是否造成損傷：{data.isDamage}</div>
            <div>是否啟動戰情：{data.operationActivated}</div>
            <div>總處理時間：{data.process_time}</div>
          </>
        )}
      </div>

      {status !== "已完成" && (
        <div className="py-3 flex justify-center">
          <button
            className={`px-4 py-2 rounded text-white ${buttonColorMap[status]}`}
            onClick={handleClick}
          >
            {actionMap[status]}
          </button>
        </div>
      )}
    </div>
  );
}
