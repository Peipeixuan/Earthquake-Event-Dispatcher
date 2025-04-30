import React from "react";

export default function EventCard({ status, data }) {
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

  return (
    <div className="bg-[#22252C] text-white rounded shadow-sm overflow-hidden">
      <div className="bg-[#23252A] border-b border-black px-4 py-2 font-semibold">
        Event ID {data.id}
      </div>

      <div className="px-4 py-4 text-sm space-y-1">
        {(status === "未接收" || status === "已完成") && (
          <>
            <div>地震時間：{data.eqTime}</div>
            <div>警報時間：{data.alertTime}</div>
            <div>芮氏規模：{data.magnitude}</div>
            <div>嚴重程度：{data.level}</div>
            {status === "已完成" && <div>最終程度：{data.finalLevel}</div>}
          </>
        )}

        {(status === "待處理" || status === "維修中" || status === "已完成") && (
          <div>接收時間：{data.receiveTime}</div>
        )}

        {status === "待處理" && (
          <>
            <div>
              是否造成損傷?：
              <label className="ml-2"><input type="radio" className="accent-amber-500" name={`success-${data.id}`} defaultChecked={data.alertSuccess === "是"} /> 是</label>
              <label className="ml-2"><input type="radio" className="accent-amber-500" name={`success-${data.id}`} defaultChecked={data.alertSuccess === "否"} /> 否</label>
            </div>
            <div>
              是否啟動戰情?：
              <label className="ml-2"><input type="radio" className="accent-amber-500" name={`device-${data.id}`} defaultChecked={data.deviceActivated === "是"} /> 是</label>
              <label className="ml-2"><input type="radio" className="accent-amber-500" name={`device-${data.id}`} defaultChecked={data.deviceActivated === "否"} /> 否</label>
            </div>
            <div>
              <a href="#" className="text-cyan-400 text-sm">更多事件資訊</a>
            </div>
          </>
        )}

        {status === "維修中" && (
          <>
            <div>戰情啟動狀態：{data.status}</div>
            <div>
              <a href="#" className="text-cyan-400 text-sm">更多事件資訊</a>
            </div>
          </>
        )}

        {status === "已完成" && (
          <>
            <div>是否造成損傷?：{data.alertSuccess}</div>
            <div>是否啟動戰情?：{data.deviceActivated}</div>
            <div>總處理時間：{data.duration}</div>
          </>
        )}
      </div>

      {status !== "已完成" && (
        <div className="py-3 flex justify-center">
          <button
            className={`px-4 py-2 rounded text-white ${buttonColorMap[status]}`}
          >
            {actionMap[status]}
          </button>
        </div>
      )}
    </div>
  );
}
