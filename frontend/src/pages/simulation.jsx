import React from "react";
import Input from "../components/input.jsx";
import { useEffect, useState } from "react";
import '../styles/simulation.css';

const data = [{
  date: "2025/04/20",
  time: "17:00:20",
  magnitude: 4,
  depth: 30,
  epicenter: "花蓮",
  intensity: { 台北: '0級', 新竹: '2級', 台中: '3級', 台南: '4級' },
},
{
  date: "2025/04/20",
  time: "17:01:10",
  magnitude: 1,
  depth: 30,
  epicenter: "花蓮",
  intensity: { 台北: '0級', 新竹: '0級', 台中: '0級', 台南: '0級' },
},
{
  date: "2025/04/20",
  time: "17:01:10",
  magnitude: 1,
  depth: 30,
  epicenter: "花蓮",
  intensity: { 台北: '0級', 新竹: '0級', 台中: '0級', 台南: '0級' },
},
{
  date: "2025/04/20",
  time: "17:01:10",
  magnitude: 1,
  depth: 30,
  epicenter: "花蓮",
  intensity: { 台北: '0級', 新竹: '0級', 台中: '0級', 台南: '0級' },
},
{
  date: "2025/04/20",
  time: "17:01:10",
  magnitude: 1,
  depth: 30,
  epicenter: "花蓮",
  intensity: { 台北: '0級', 新竹: '0級', 台中: '0級', 台南: '0級' },
},
{
  date: "2025/04/20",
  time: "17:01:10",
  magnitude: 1,
  depth: 30,
  epicenter: "花蓮",
  intensity: { 台北: '0級', 新竹: '0級', 台中: '0級', 台南: '0級' },
},
{
  date: "2025/04/20",
  time: "17:01:10",
  magnitude: 1,
  depth: 30,
  epicenter: "花蓮",
  intensity: { 台北: '0級', 新竹: '0級', 台中: '0級', 台南: '0級' },
},
{
  date: "2025/04/20",
  time: "17:01:10",
  magnitude: 1,
  depth: 30,
  epicenter: "花蓮",
  intensity: { 台北: '0級', 新竹: '0級', 台中: '0級', 台南: '0級' },
},
{
  date: "2025/04/20",
  time: "17:01:10",
  magnitude: 1,
  depth: 30,
  epicenter: "花蓮",
  intensity: { 台北: '0級', 新竹: '0級', 台中: '0級', 台南: '0級' },
},
{
  date: "2025/04/20",
  time: "17:01:10",
  magnitude: 1,
  depth: 30,
  epicenter: "花蓮",
  intensity: { 台北: '0級', 新竹: '0級', 台中: '0級', 台南: '0級' },
},
{
  date: "2025/04/20",
  time: "17:01:10",
  magnitude: 1,
  depth: 30,
  epicenter: "花蓮",
  intensity: { 台北: '0級', 新竹: '0級', 台中: '0級', 台南: '0級' },
},
{
  date: "2025/04/20",
  time: "17:01:10",
  magnitude: 1,
  depth: 30,
  epicenter: "花蓮",
  intensity: { 台北: '0級', 新竹: '0級', 台中: '0級', 台南: '0級' },
},
{
  date: "2025/04/20",
  time: "17:01:10",
  magnitude: 1,
  depth: 30,
  epicenter: "花蓮",
  intensity: { 台北: '0級', 新竹: '0級', 台中: '0級', 台南: '0級' },
},
{
  date: "2025/04/20",
  time: "17:01:10",
  magnitude: 1,
  depth: 30,
  epicenter: "花蓮",
  intensity: { 台北: '0級', 新竹: '0級', 台中: '0級', 台南: '0級' },
},
{
  date: "2025/04/20",
  time: "17:01:10",
  magnitude: 1,
  depth: 30,
  epicenter: "花蓮",
  intensity: { 台北: '0級', 新竹: '0級', 台中: '0級', 台南: '0級' },
}
]


const fetchEarthquakeData = () => {
  return Promise.resolve([
    {
      date: "2025/04/20",
      time: "17:00:20",
      magnitude: 4,
      depth: 30,
      epicenter: "花蓮",
      intensity: { 台北: 3, 新竹: 3, 台中: 2, 台南: 3 },
    },
    {
      date: "2025/04/20",
      time: "17:01:10",
      magnitude: 1,
      depth: 30,
      epicenter: "花蓮",
      intensity: { 台北: 0, 新竹: 1, 台中: 1, 台南: 1 },
    },
    // 你可以加更多 rows
  ]);
};



const getIntensityColor = (value) => {
  if (value == '0級' || value == '1級') return "bg-emerald-700";
  if (value == '2級') return "bg-amber-600";
  return "bg-red-800";
};

export default function Simulation() {

  const [hours, setHours] = useState(0);  // 小時
  const [minutes, setMinutes] = useState(10);  // 分鐘
  const [seconds, setSeconds] = useState(0);  // 秒數

  // 當用戶選擇小時、分鐘、秒數時更新狀態
  const handleChange = (type, value) => {
    if (type === "hours") setHours(value);
    if (type === "minutes") setMinutes(value);
    if (type === "seconds") setSeconds(value);
  };

  // 顯示的時間格式
  const timeString = `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;

  return (
    <div className="min-h-screen bg-zinc-900 text-white p-6 space-y-8">
      <h2 className="text-xl font-bold">調整警報抑制時間</h2>
      <div className="flex flex-col md:flex-row gap-4">
      {/* 調整警報抑制時間 */}
      <section className="flex gap-4">
        <Input title="設定時間">
        {/* 小時下拉選單 */}
      <select
        value={hours}
        onChange={(e) => handleChange("hours", e.target.value)}
        className="bg-transparent text-white border-none focus:ring-0 w-10 mr-2"
      >
        {[...Array(24).keys()].map((hour) => (
          <option key={hour} value={hour}>{String(hour).padStart(2, "0")}</option>
        ))}
      </select>:

      {/* 分鐘下拉選單 */}
      <select
        value={minutes}
        onChange={(e) => handleChange("minutes", e.target.value)}
        className="bg-transparent text-white border-none focus:ring-0 w-10 mr-2"
      >
        {[...Array(60).keys()].map((minute) => (
          <option key={minute} value={minute}>{String(minute).padStart(2, "0")}</option>
        ))}
      </select>:

      {/* 秒數下拉選單 */}
      <select
        value={seconds}
        onChange={(e) => handleChange("seconds", e.target.value)}
        className="bg-transparent text-white border-none focus:ring-0 w-10 mr-4"
      >
        {[...Array(60).keys()].map((second) => (
          <option key={second} value={second}>{String(second).padStart(2, "0")}</option>
        ))}
      </select>
      </Input>
      <button className="w-36 bg-sky-500 hover:bg-sky-600 text-white px-4 py-2 rounded">送出</button>

      </section>

      </div>

      {/* 模擬地震 */}
      <section className="space-y-3">
        <h2 className="text-xl font-bold">模擬地震</h2>
        <div className="flex flex-col md:flex-row gap-4">
          {/* <div class="col-span-2"> */}
          <Input title="時間">
            <div className="relative flex items-center gap-1">
              <input
                type="datetime-local"
                defaultValue="2025-04-21T17:30:02"
                className="bg-transparent border-none text-white focus:ring-0 appearance-none pr-8 datetime-picker"
              />
              <div className="absolute right-2">
                <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4 text-blue-400 pointer-events-none" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
            </div>
          </Input>
          {/* </div> */}

          <Input title="芮氏規模">
            <select
                className="bg-transparent border-none text-white focus:ring-0"
                defaultValue="5"
              >                
                <option value="2">2</option>
                <option value="3">3</option>
                <option value="4">4</option>
                <option value="5">5</option>
                <option value="6">6</option>
                <option value="7">7</option>
                <option value="8">8</option>
                <option value="9">9</option>
                
              </select>
          </Input>
          <Input title="深度">
            <div className="flex items-center gap-2">
              <input
                type="number"
                defaultValue="25"
                className="bg-transparent border-none text-white focus:ring-0 w-20"
              />
              <span className="text-blue-400 text-sm">km</span>
            </div>
          </Input>
          <Input title="震央">
            <select
              className="bg-transparent border-none text-white focus:ring-0"
              defaultValue="Hualien"
            >
              <option value="花蓮">花蓮</option>
              <option value="台北">台北</option>
              <option value="台南">台南</option>
            </select>
          </Input>
        </div>
        <div className="flex flex-col md:flex-row gap-4">
          {['台北', '新竹', '台中', '台南'].map(city => (
            <div key={city} className="flex space-x-2">
              <Input title={`${city}震度`}>
              <select
                className="bg-transparent border-none text-white focus:ring-0"
                defaultValue="3級"
              >
                <option value="0級">0級</option>
                <option value="1級">1級</option>
                <option value="2級">2級</option>
                <option value="3級">3級</option>
                <option value="4級">4級</option>
                <option value="5弱">5弱</option>
                <option value="5強">5強</option>
                <option value="6弱">6弱</option>
                <option value="6強">6強</option>
                <option value="7級">7級</option>
              </select>
            </Input>
            </div>
          ))}
          <button className="w-36 bg-sky-500 hover:bg-sky-600 text-white px-4 py-2 rounded">送出</button>
        </div>
        
      </section>

      {/* 歷史紀錄 */}
      <section>
        <h2 className="text-xl font-bold mb-2">歷史紀錄</h2>
        <div className="max-h-[500px] min-w-full">
          <table className="max-h-44 min-w-full text-sm border-separate border-spacing-y-1 text-left border border-neutral-900">
            <thead className="bg-neutral-800 w-full sticky block">
              <tr>
                {["日期", "時間", "芮氏規模", "深度 (km)", "震央", "台北震度", "新竹震度", "台中震度", "台南震度"].map(header => (
                  <th key={header} className="w-40 top-0 px-4 py-2 font-semibold text-sky-500 bg-neutral-800">{header}</th>
                ))}
              </tr>
            </thead>
            <tbody className="overflow-y-auto min-w-full block max-h-[400px]">
                {data.map((row, idx) => (
                <tr key={idx} className="bg-neutral-900 ">
                  <td className="w-40 px-4 py-2">{row.date}</td>
                  <td className="w-40 px-4 py-2">{row.time}</td>
                  <td className="w-40 px-4 py-2">{row.magnitude}</td>
                  <td className="w-40 px-4 py-2">{row.depth}</td>
                  <td className="w-40 px-4 py-2">{row.epicenter}</td>
                  {Object.entries(row.intensity).map(([city, value]) => (
                    <td
                      key={city}
                      className={`w-40 px-4 py-2 ${getIntensityColor(value)}`}
                    >
                      {value}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
            
          </table>
        </div>
      </section>
    </div>
  );
}