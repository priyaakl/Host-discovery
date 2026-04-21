# 🌐 SDN Host Discovery with Dynamic Updates  

---

## 👩‍💻 Student Details  
**Name:** PRIYA K L  
**SRN:** PES1UG24CS600  

---

## 📌 Problem Statement  

This project implements a **Host Discovery System in Software Defined Networking (SDN)** using **Mininet** and the **Ryu Controller (OpenFlow 1.3)**.

The controller dynamically discovers hosts by analyzing **ARP packets** and maintains a **real-time host table**.

### 🔄 The system automatically updates when:
- 🟢 New hosts are detected  
- 🔴 Links go down *(hosts removed)*  
- 🟢 Links come back up *(hosts re-added)*  

---

## ✨ Key Features  

- 🚀 Dynamic host discovery *(no predefined configuration)*  
- 📡 Real-time host table updates  
- 🔍 ARP-based detection *(IP + MAC learning)*  
- 🔴 Automatic removal on link down  
- 🟢 Re-discovery on link up  
- 🔁 Fresh state after every Mininet restart  
- 📝 Host logging using `hosts.log`  
- 🎯 Centralized monitoring using Ryu controller  

---

## 🌐 Topology  

```
     h1     h2     h3
      |      |      |
      +-------------+
             s1
             |
             |
             s2
           /    \
         h4      h5
```

---

## 🔗 Connections  

```
(h1, s1) (h2, s1) (h3, s1)
(h4, s2) (h5, s2)
(s1, s2)
```

---

## 📁 Project Structure  

```
SDN-project/
├── host_discovery.py  
├── host_db.py  
├── topology.py  
├── hosts.log  
└── README.md
```

---

## ⚙️ How It Works  

1. 📥 Switch sends packets to controller  
2. 🔍 Controller filters ARP packets  
3. 📊 Extracts:
   - IP address  
   - MAC address  
   - Switch (DPID)  
   - Port number  
4. ➕ Adds new host to database  
5. 🖥️ Prints and logs updated host table  

---

## 🚀 Execution Steps  

### ▶️ Step 1 — Start Ryu Controller  

```bash
python3 -m ryu.cmd.manager host_discovery.py
```

---

### ▶️ Step 2 — Start Mininet Topology  

```bash
sudo mn --custom topology.py --topo mytopo --controller remote --switch ovsk,protocols=OpenFlow13
```

---

### ▶️ Step 3 — Trigger Host Discovery  

```bash
pingall
```

---

## 🔄 Dynamic Updates  

### 🔻 Link Down (Remove Host)  

```bash
link s1 h1 down
```

✔ Host is removed from host table  

---

### 🔺 Link Up (Re-add Host)  

```bash
link s1 h1 up
h1 ping -c 1 h2
```

✔ Host is rediscovered and added back  

---

## 🔁 Restart Behavior  

```bash
exit
sudo mn -c
sudo mn --custom topology.py --topo mytopo --controller remote --switch ovsk,protocols=OpenFlow13
```

✔ Old hosts are cleared  
✔ Fresh host table is created  

---

## 📄 Logs  

```bash
cat hosts.log
```

---

# 📸 Output Screenshots  

---

## 🟢 1. Initial Host Discovery  

### 📌 Mininet Output  
<img src="https://github.com/user-attachments/assets/290941b9-41da-4510-84b7-8fd2917c083f" width="700"/>

### 📌 Host Discovery Output  
<img src="https://github.com/user-attachments/assets/7b6815e8-a945-495b-9eb7-b52599af4ded" width="700"/>

---

## 🔴 2. Link Down (Host Removed)  

### 📌 Mininet Output  
<img src="https://github.com/user-attachments/assets/1efaae93-1d51-4741-8151-653454672309" width="700"/>

### 📌 Host Discovery Output  
<img src="https://github.com/user-attachments/assets/3eeb6795-7109-45f1-b0b6-09e86128c361" width="700"/>

---

## 🟢 3. Link Up (Host Re-added)  

### 📌 Mininet Output  
<img src="https://github.com/user-attachments/assets/9de911c7-70b2-4489-b98c-8234c542152c" width="700"/>

### 📌 Host Discovery Output  
<img src="https://github.com/user-attachments/assets/07b3ffd8-c2dc-426f-950d-5b7b5168d370" width="700"/>

---

## 🔁 4. Fresh Run (No Old Hosts)  

### 📌 Mininet Output  
<img src="https://github.com/user-attachments/assets/bf905b9a-4d0e-41f9-882a-2146aa351551" width="700"/>

### 📌 Host Discovery Output  
<img src="https://github.com/user-attachments/assets/68954cfd-80cb-4bbe-9f11-c8b29f91c9b7" width="700"/>

---

## 📄 5. Log File Output  

<img src="https://github.com/user-attachments/assets/0748ba2c-3d23-4e49-9f27-f47c7fcb2283" width="700"/>

---

## 📊 Expected Behavior  

| Scenario            | Result |
|-------------------|--------|
| Initial run        | All hosts detected |
| Link down          | Host removed |
| Link up            | Host re-added |
| Restart Mininet    | Fresh host table |

---

## ✅ Conclusion  

This project demonstrates:

- 🌐 Dynamic host discovery using SDN  
- ⚡ Real-time topology awareness  
- 🔄 Automatic adaptation to network changes  
- 🎯 Centralized control using Ryu  

The system ensures that the host table always reflects the **current network state**, making it suitable for real-time network monitoring.
