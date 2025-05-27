import React from "react";
import Input from "../components/input.jsx";
import { useEffect, useState } from "react";
import '../styles/simulation.css';
import axiosInstance from '../axiosInstance';
import { API_SIMULATE, API_ALERT_SUPPRESS, API_SIMULATE_GET } from "../globals/constants.js";
import { state_longtitude_lantitude } from "../globals/geo.js";

const cityNameMap = {
  "台北": "Taipei",
  "新竹": "Hsinchu",
  "台中": "Taichung",
  "台南": "Tainan",
};

const getIntensityColor = (value) => {
  if (value == 0 || value == 1) return "bg-emerald-700";
  if (value == 2) return "bg-amber-600";
  return "bg-red-800";
};

const getLocalDatetimeStringWithSeconds = () => {
  const now = new Date();
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
  return now.toISOString().slice(0, 19);
};

export default function Simulation() {

  const [hours, setHours] = useState(0);
  const [minutes, setMinutes] = useState(0);

  const [earthquakeData, setEarthquakeData] = useState({
    earthquake_time: getLocalDatetimeStringWithSeconds(),
    magnitude: 5,
    depth: 25,
    center: "花蓮縣",
    longitude: state_longtitude_lantitude["花蓮縣"][0],
    latitude: state_longtitude_lantitude["花蓮縣"][1],
    intensities: {
      台北: 0,
      新竹: 0,
      台中: 0,
      台南: 0,
    },
  });

  // 歷史模擬紀錄
  const [simulateData, setSimulateData] = useState([]);

  useEffect(() => {
    document.title = "地震模擬系統";
    fetchSimulateData();
    fetchSuppressData();
  }, []);

  // 獲取模擬數據
  const fetchSimulateData = async () => {
    try {
      const response = await axiosInstance.get(API_SIMULATE_GET); 
      console.log("取得模擬資料：", response.data);
      setSimulateData(response.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const fetchSuppressData = async () => {
    try {
      const response = await axiosInstance.get(API_ALERT_SUPPRESS);
      console.log(response.data); 
      const totalMins = response.data['alert_suppress_time'] || 0;
      const hh = Math.floor(totalMins / 60);
      const mm = totalMins % 60;
      const ss = 0; // 假設秒數為 0
      setHours(hh);
      setMinutes(mm);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const handleEarthquakeChange = (field, value, city = null) => {
    if (city) {
      // 更新 intensities 裡對應城市的震度
      const intensity = parseFloat(value);
      setEarthquakeData((prev) => ({
        ...prev,
        intensities: {
          ...prev.intensities,
          [city]: intensity,
        },
      }));
    } else if (field === "center") {
      // 同時更新 center、latitude、longitude
      const [longitude, latitude] = state_longtitude_lantitude[value] || [null, null];
      setEarthquakeData((prev) => ({
        ...prev,
        center: value,
        longitude,
        latitude,
      }));
    } else {
      // 一般欄位更新（例如：earthquake_time, magnitude, depth）
      setEarthquakeData((prev) => ({
        ...prev,
        [field]: value,
      }));
    }
  };

  const handleSubmitSimulate = async () => {
    const { earthquake_time, magnitude, depth, center, latitude, longitude, intensities } = earthquakeData;

    // 檢查是否早於現在一小時前
    const simulateTime = new Date(earthquake_time);
    const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000);

    if (simulateTime < oneHourAgo) {
      alert("禁止模擬一小時前的地震！");
      return; // 中止提交
    }
  
    const payload = {
      earthquake: {
        // earthquake_id: 0, 
        earthquake_time,
        center,
        latitude: latitude?.toString() || "",
        longitude: longitude?.toString() || "",
        magnitude: parseFloat(magnitude),
        depth: parseFloat(depth),    
        is_demo: true,
      },
      locations: Object.entries(intensities).map(([location, intensity]) => ({
        location: cityNameMap[location] || location,
        intensity: intensity,
      })),
    };

    console.log("Final Payload:", JSON.stringify(payload, null, 2));
    console.log("axios baseURL:", axiosInstance.defaults.baseURL);
  
    try {
      const response = await axiosInstance.post(API_SIMULATE, payload);
      console.log("POST response:", response.data);
      alert("模擬地震數據已成功提交！");
      await fetchSimulateData();
    } catch (error) {
      console.error("Error submitting data:", error);
      alert("提交失敗，請稍後再試！");
    }
  };

  const handleSubmitSuppress = async () => {
    const totalMins = parseInt(hours) * 60 + parseInt(minutes);
    const payload = {
      'alert_suppress_time': totalMins
    };
  
    try {
      const response = await axiosInstance.post(API_ALERT_SUPPRESS, payload, { params: payload });
      console.log("POST response:", response.data);
      alert("抑制時間已成功提交！");
    } catch (error) {
      console.error("Error submitting data:", error);
      alert("提交失敗，請稍後再試！");
    }
  };

  // 當用戶選擇小時、分鐘、秒數時更新狀態
  const handleChange = (type, value) => {
    if (type === "hours") setHours(value);
    if (type === "minutes") setMinutes(value);
  };

  // 顯示的時間格式
  const timeString = `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}`;

  return (
    <div className="min-h-screen bg-zinc-900 text-white p-6 space-y-8">
      <a
        href="http://34.81.36.176/grafana/d/0a4725e4-1260-4f2f-826c-d1ae7ad637f9/earthquake-event-dispatcher?orgId=1&from=now-6h&to=now&timezone=browser&var-region=$__all" className="hover:underline">
        &lt;&lt; Back To Dashboard
      </a>

      <h2 className="text-xl font-bold">調整警報抑制時間</h2>
      <div className="flex flex-col md:flex-row gap-4">
      {/* 調整警報抑制時間 */}
      <section className="flex gap-4">
        <Input title="設定時間">
        {/* 小時下拉選單 */}
      <select
        value={hours}
        onChange={(e) => handleChange("hours", e.target.value)}
        className="bg-zinc-900 text-white px-4 py-2 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-500 text-sm [&>option]:bg-zinc-800 select-scrollbar"
      >
        {[...Array(24).keys()].map((hour) => (
          <option key={hour} value={hour}>{String(hour).padStart(2, "0")}</option>
        ))}
      </select>:

      {/* 分鐘下拉選單 */}
      <select
        value={minutes}
        onChange={(e) => handleChange("minutes", e.target.value)}
        className="bg-zinc-900 text-white px-4 py-2 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-500 text-sm [&>option]:bg-zinc-800 select-scrollbar"
      >
        {[...Array(60).keys()].map((minute) => (
          <option key={minute} value={minute}>{String(minute).padStart(2, "0")}</option>
        ))}
      </select>

      </Input>
      <button onClick={handleSubmitSuppress} className="w-36 bg-sky-500 hover:bg-sky-600 text-white px-4 py-2 rounded">送出</button>

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
                value={earthquakeData.earthquake_time}
                onChange={(e) => handleEarthquakeChange("earthquake_time", e.target.value)}
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
              value={earthquakeData.magnitude}
              onChange={(e) => handleEarthquakeChange("magnitude", e.target.value)}
              className="bg-zinc-900 text-white px-4 py-2 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-500 text-sm [&>option]:bg-zinc-800"
            >
              {[...Array(8).keys()].map((i) => (
                <option key={i + 2} value={i + 2}>
                  {i + 2}
                </option>
              ))}
            </select>
          </Input>
          <Input title="深度">
            <div className="flex items-center gap-2">
              <input
                type="number"
                value={earthquakeData.depth}
                onChange={(e) => handleEarthquakeChange("depth", e.target.value)}
                className="bg-transparent border-none text-white focus:ring-0 w-20"
              />
              <span className="text-blue-400 text-sm">km</span>
            </div>
          </Input>
          <Input title="震央">
            <select
              className="bg-zinc-900 text-white px-4 py-2 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-500 text-sm [&>option]:bg-zinc-800 select-scrollbar"
              value={earthquakeData.center}
              onChange={(e) => handleEarthquakeChange("center", e.target.value)}
            >
              {Object.keys(state_longtitude_lantitude).map(location => (
                <option key={location} value={location}>{location}</option>
              ))}
            </select>
          </Input>
        </div>
        <div className="flex flex-col md:flex-row gap-4">
          {['台北', '新竹', '台中', '台南'].map(city => (
            <div key={city} className="flex space-x-2">
              <Input title={`${city}震度`}>
              <select
                value={earthquakeData.intensities[city]}
                onChange={(e) => handleEarthquakeChange("intensity", e.target.value, city)}
                className="bg-zinc-900 text-white px-4 py-2 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-500 text-sm [&>option]:bg-zinc-800"
              >
                <option value="0">0級</option>
                <option value="1">1級</option>
                <option value="2">2級</option>
                <option value="3">3級</option>
                <option value="4">4級</option>
                <option value="5">5弱</option>
                <option value="5.5">5強</option>
                <option value="6">6弱</option>
                <option value="6.5">6強</option>
                <option value="7">7級</option>
              </select>
            </Input>
            </div>
          ))}
          <button className="w-36 bg-sky-500 hover:bg-sky-600 text-white px-4 py-2 rounded" onClick={handleSubmitSimulate}>送出</button>
        </div>
        
      </section>

      {/* 歷史紀錄 */}
      <section>
        <h2 className="text-xl font-bold mb-2">歷史紀錄</h2>
        <div className="max-h-[500px] min-w-full">
          <table className="max-h-44 min-w-full text-sm border-separate border-spacing-y-1 text-left border border-neutral-900">
            <thead className="bg-neutral-800 w-full sticky block">
              <tr className="block">
                <div className="flex min-w-full">
                {["時間", "芮氏規模", "深度 (km)", "震央", "台北震度", "新竹震度", "台中震度", "台南震度"].map(header => (
                  <th key={header} className="w-1/6 top-0 px-4 py-2 font-semibold text-sky-500 bg-neutral-800">{header}</th>
                ))}
                </div>
              </tr>
            </thead>
            <tbody className="overflow-y-auto min-w-full block max-h-[400px] table-scrollbar">
              {simulateData.map((row, idx) => {
                const { earthquake, locations } = row;
                const intensityMap = {};
                locations.forEach(({ location, intensity }) => {
                  const chineseLocation = Object.keys(cityNameMap).find(city => cityNameMap[city] === location) || location;
                  intensityMap[chineseLocation] = intensity;
                });

                return (
                  <tr key={idx} className="bg-neutral-900 flex border-b border-zinc-900">
                    <td className="w-1/6 px-4 py-2">{earthquake.earthquake_time.replace("T", " ")}</td>
                    <td className="w-1/6 px-4 py-2">{earthquake.magnitude}</td>
                    <td className="w-1/6 px-4 py-2">{earthquake.depth}</td>
                    <td className="w-1/6 px-4 py-2">{earthquake.center}</td>
                    {["台北", "新竹", "台中", "台南"].map((city) => (
                      <td
                        key={city}
                        className={`w-1/6 px-4 py-2 border-r border-zinc-900 ${getIntensityColor(intensityMap[city])}`}
                      >
                        {intensityMap[city]}
                      </td>
                    ))}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}