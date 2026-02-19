// src/api.js
import axios from "axios";

const API_BASE = "http://localhost:8000"; // change to your deployed backend

export const analyzeVCF = async (file, drugs) => {
  const formData = new FormData();
  formData.append("file", file);
  // accept array or string
  const drugString = Array.isArray(drugs) ? drugs.join(",") : (drugs || "");
  formData.append("drug", drugString);

  const res = await axios.post(`${API_BASE}/analyze`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
    timeout: 120000,
  });

  return res.data;
};

export const generateClinicalReport = async (results) => {

  const payload = Array.isArray(results)
    ? results
    : [results];

  const res = await axios.post(
    `${API_BASE}/report/`,
    payload,
    {
      responseType: "blob",
      timeout: 120000,
    }
  );

  return res.data;
};
