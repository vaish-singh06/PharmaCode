// src/components/Loader.js
import React from "react";

const Loader = ({ label = "Analyzing" }) => {
  return (
    <div className="pg-loader">
      <div className="pg-loader-dna">
        <div className="dna-bar" />
        <div className="dna-bar" />
        <div className="dna-bar" />
        <div className="dna-bar" />
        <div className="dna-bar" />
      </div>

      <div className="pg-loader-text">
        {label}
        <span className="dot">.</span>
        <span className="dot">.</span>
        <span className="dot">.</span>
      </div>
    </div>
  );
};

export default Loader;