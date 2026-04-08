import React, { useEffect, useState } from 'react';
import styles from '../styles/FlashMessage.module.css';

export default function FlashMessage({ text, color }) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (text) {
      setVisible(true);
      const timer = setTimeout(() => setVisible(false), 1000);
      return () => clearTimeout(timer);
    }
  }, [text]);

  return (
    <div
      className={`${styles.flash} ${visible ? styles.visible : ''}`}
      style={{ color }}
    >
      {text}
    </div>
  );
}
