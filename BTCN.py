import tkinter as tk
from tkinter import ttk
from collections import deque
from tkinter import messagebox
import time
import random
import math
import heapq
import numpy as np


class ChessSolver:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Giao dien Place N Rooks")
        self.root.geometry("1100x800")

        # Khởi tạo các biến trạng thái
        self.size = 8
        self.leftButton = []
        self.rightButton = []
        self.currentChess = []
        self.currentPositions = []
        self.stopFlag = False
        self.bfsPosition = [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7)]
        self.dfsPosition = [(0, 0), (7, 1), (6, 2), (5, 3), (4, 4), (3, 5), (2, 6), (1, 7)]
        self.costLabel = None
        self.currentCost = 0
        self.speed = 0.02

        # Khởi tạo UI
        self.setupUI()

    def setupUI(self):
        # Tạo frame chính chứa 2 bàn cờ
        self.mainFrame = tk.Frame(self.root, bg="white")
        self.mainFrame.pack(fill="both", expand=True, padx=10, pady=10)

        # Tạo bàn cờ trái và phải
        self.createLB()
        self.createRB()

        # Tạo frame các button
        self.controlPanel()

        # Tạo khung log
        self.createLogPanel()

    def createLB(self):
        # Tạo bàn cờ bên trái
        self.leftFrame = tk.Frame(self.mainFrame, bg="white")
        self.leftFrame.pack(side="left", fill="both", expand=True, padx=10)
        self.leftLabel = tk.Label(self.leftFrame, text="Ban co trong",
                                  font=("Arial", 12, "bold"), bg="white")
        self.leftLabel.pack(pady=3)
        self.leftBoard = tk.Frame(self.leftFrame, bg="black", bd=2, relief="solid")
        self.leftBoard.pack(fill="both", expand=True)

        # Configure grid để expand
        for i in range(self.size):
            self.leftBoard.grid_rowconfigure(i, weight=1, minsize=50)
            self.leftBoard.grid_columnconfigure(i, weight=1, minsize=50)

        # Tạo các ô cho bàn cờ trái
        for i in range(self.size):
            rowButtons1 = []
            for j in range(self.size):
                bgColor = "black" if (i + j) % 2 == 0 else "white"

                button1 = tk.Button(self.leftBoard, text=' ',
                                    bg=bgColor, relief="solid", bd=1,
                                    font=("Arial", 10, "bold"),
                                    width=3, height=1)

                button1.grid(row=i, column=j, sticky="nsew", padx=0, pady=0)
                button1.configure(command=lambda row=i, col=j: self.placeChess(row, col))
                rowButtons1.append(button1)

            self.leftButton.append(rowButtons1)

    def createRB(self):
        # Tạo bàn cờ bên phải
        self.rightFrame = tk.Frame(self.mainFrame, bg="white")
        self.rightFrame.pack(side="right", fill="both", expand=True, padx=10)
        self.rightLabel = tk.Label(self.rightFrame, text="Ban co muc tieu",
                                   font=("Arial", 12, "bold"), bg="white")
        self.rightLabel.pack(pady=3)
        self.rightBoard = tk.Frame(self.rightFrame, bg="black", bd=2, relief="solid")
        self.rightBoard.pack(fill="both", expand=True)

        # Configure grid để expand
        for i in range(self.size):
            self.rightBoard.grid_rowconfigure(i, weight=1, minsize=50)
            self.rightBoard.grid_columnconfigure(i, weight=1, minsize=50)

        # Tạo các ô cho bàn cờ phải
        for i in range(self.size):
            rowButtons2 = []
            for j in range(self.size):
                bgColor = "black" if (i + j) % 2 == 0 else "white"

                button2 = tk.Button(self.rightBoard, text=' ',
                                    bg=bgColor, relief='solid', bd=1,
                                    font=('Arial', 10, 'bold'),
                                    width=3, height=1)

                # Kiểm tra vị trí đặt quân hậu
                if (i, j) in self.bfsPosition:
                    button2.configure(text='♜', fg='red')

                button2.grid(row=i, column=j, sticky="nsew", padx=0, pady=0)
                button2.configure(command=lambda row=i, col=j: self.placePosition(row, col))
                rowButtons2.append(button2)
            self.currentPositions = self.bfsPosition
            self.rightButton.append(rowButtons2)

    def controlPanel(self):
        # Tạo panel điều khiển
        self.btnFrame = tk.Frame(self.root, bg="white")
        self.btnFrame.pack(padx=10, pady=5)

        # Nút Reset
        self.resetButton = tk.Button(self.btnFrame, text="Reset", bg="white", fg="black",
                                     font=("Arial", 14, "bold"), command=self.resetLB)
        self.resetButton.pack(side="left", pady=5)


        # ComboBox chọn thuật toán
        choiceAgorithm = ["BFS", "DFS", "UCS", "DLS", "IDS",
                          "Greedy Search", "A* Search",
                          "Hill Climbing", "Simulated Annealing", "Beam Search", "Genetic Algorithm",
                          "Recursive AND-OR Tree Search (DFS)", "Recursive AND-OR Tree Search (DFS) -- Non-Deterministic"
                          "BFS No Observation With Beliefs", "BFS Partial Observation With Beliefs",
                          "CSP", "CSP-AC3"]
        self.tt = tk.StringVar()
        self.choiceBox = ttk.Combobox(self.btnFrame, values=choiceAgorithm,
                                      font=("Arial", 12, "bold"), textvariable=self.tt, width=25, state="readonly")
        self.choiceBox.current(0)
        self.choiceBox.pack(side="left", padx=5)
        self.choiceBox.bind("<<ComboboxSelected>>", self.updateRB)


        # Nút Run
        self.controlButton = tk.Button(self.btnFrame, text="Run", bg="white", fg="black",
                                       font=("Arial", 14, "bold"), command=self.controlSolution)
        self.controlButton.pack(side="left", pady=5)

        # Nút Stop
        self.stopButton = tk.Button(self.btnFrame, text="Stop", bg="red", fg="white",
                                    font=("Arial", 14, "bold"), command=self.stop)
        self.stopButton.pack(side="left", padx=5)

    def createLogPanel(self):
        # Tạo khung log ở dưới cùng
        self.logFrame = tk.Frame(self.root, bg="white")
        self.logFrame.pack(fill="both", expand=True, padx=10, pady=5)

        # Label cho log
        self.logLabel = tk.Label(self.logFrame, text="Log thông tin:",
                                 font=("Arial", 10, "bold"), bg="white", anchor="w")
        self.logLabel.pack(fill="x")

        # Text widget để hiển thị log với scrollbar
        logContainer = tk.Frame(self.logFrame, bg="white")
        logContainer.pack(fill="both", expand=True)

        self.logScrollbar = tk.Scrollbar(logContainer)
        self.logScrollbar.pack(side="right", fill="y")

        self.logText = tk.Text(logContainer, height=3, font=("Consolas", 9),
                               bg="#f5f5f5", fg="black", relief="solid", bd=1,
                               yscrollcommand=self.logScrollbar.set, wrap="word")
        self.logText.pack(side="left", fill="both", expand=True)
        self.logScrollbar.config(command=self.logText.yview)

        # Disable editing
        self.logText.config(state="disabled")

    # Hàm helper để thêm log
    def addLog(self, message):
        self.logText.config(state="normal")
        self.logText.insert("end", f"{message}\n")
        self.logText.see("end")  # Auto scroll to bottom
        self.logText.config(state="disabled")

    def clearLog(self):
        self.logText.config(state="normal")
        self.logText.delete(1.0, "end")
        self.logText.config(state="disabled")

    def placeChess(self, row, col):
        # Xử lý sự kiện click bàn cờ trái
        if (row, col) in self.currentChess:
            self.currentChess.remove((row, col))
        else:
            self.currentChess.append((row, col))

        return self.leftButton[row][col].configure(
            text=' ' if (row, col) not in self.currentChess else '♜',
            fg='black' if (row, col) not in self.currentChess else 'red',
        )

    def placePosition(self, row, col):
        # Xử lý sự kiện click bàn cờ phải
        if (row, col) in self.currentPositions:
            self.currentPositions.remove((row, col))
        else:
            self.currentPositions.append((row, col))

        return self.rightButton[row][col].configure(
            text=' ' if (row, col) not in self.currentPositions else '♜',
            fg='black' if (row, col) not in self.currentPositions else 'red'
        )

    def resetLB(self):
        self.currentChess = []
        for row in self.leftButton:
            for button in row:
                button.configure(text='', fg='black', font=("Arial", 14, "bold"))

        # Reset chi phí về 0
        if self.costLabel:
            self.costLabel.configure(text="0", fg="green")

    def updateRB(self, event=None):
        # Cập nhật bàn cờ mục tiêu khi chọn thuật toán
        # Reset bàn cờ phải
        self.currentPositions = []
        for i in range(8):
            for j in range(8):
                self.rightButton[i][j].configure(text=' ', fg='red')

        # Cập nhật theo thuật toán được chọn
        if self.tt.get() == "BFS":
            self.currentPositions = self.bfsPosition
        elif self.tt.get() == "DFS":
            self.currentPositions = self.bfsPosition
        elif self.tt.get() == "UCS":
            self.currentPositions = self.bfsPosition
        elif self.tt.get() == "DLS":
            self.currentPositions = self.bfsPosition
        elif self.tt.get() == "Greedy Search":
            self.currentPositions = self.bfsPosition
        elif self.tt.get() == "A* Search":
            self.currentPositions = self.bfsPosition
        elif self.tt.get() == "Hill Climbing":
            self.currentPositions = self.bfsPosition
        elif self.tt.get() == "Simulated Annealing":
            self.currentPositions = self.bfsPosition
        else:
            self.currentPositions = []


        self.currentPositions.sort(key=lambda x: x[0])
        # Cập nhật lại bàn cờ trái
        for (r, c) in self.currentPositions:
            self.rightButton[r][c].configure(text='♜', fg='red')

    def stop(self):
        self.stopFlag = True

    def cost(self, state):
        # Tính chi phí
        costValue = 0
        for r, c in state:
            for (a, b) in self.bfsPosition:
                if c == b:
                    costValue += abs(a - r) + abs(b - c)

        n = len(self.currentPositions)
        if len(state) < n:
            costValue += n - len(state)

        return costValue

    def costMahattan(self, state):
        # chi phí càng thấp càng tốt
        costValue = 0
        for (r, c) in state:
            for (a, b) in self.currentPositions:
                costValue += abs(a - r) + abs(b - c)
        return costValue

    def costChebyshev(self, state):
        # chi phí càng thấp càng tốt
        costValue = 0
        for (r, c) in state:
            for (a, b) in self.currentPositions:
                costValue += max(abs(a - r), abs(b - c))
        return costValue

    def updateCostDisplay(self, state):
        # Cập nhật hiển thị chi phí
        currentCost = self.cost(state)
        self.costLabel.configure(text=f"{currentCost}")

        # Đổi màu theo mức độ chi phí
        if currentCost == 0:
            color = "green"
        elif currentCost < 5:
            color = "blue"
        elif currentCost < 8:
            color = "orange"
        else:
            color = "red"
        self.costLabel.configure(fg=color)

    def controlSolution(self):
        # Cập nhật theo thuật toán được chọn
        if self.tt.get() == "BFS":
            self.bfsdfsSolution()
        elif self.tt.get() == "DFS":
            self.bfsdfsSolution()
        elif self.tt.get() == "UCS":
            self.ucsSolution()
        elif self.tt.get() == "DLS":
            self.dlsSolution()
        elif self.tt.get() == "IDS":
            self.idsSolution()
        elif self.tt.get() == "Greedy Search":
            self.greedySolution()
        elif self.tt.get() == "A* Search":
            self.aStarSolution()
        elif self.tt.get() == "Hill Climbing":
            self.hillClimbing()
        elif self.tt.get() == "Simulated Annealing":
            self.simulatedAnnealing()
        elif self.tt.get() == "Beam Search":
            self.beamSearch()
        elif self.tt.get() == "Genetic Algorithm":
            self.geneticAlgorithm()
        elif self.tt.get() == "Recursive AND-OR Tree Search (DFS)":
            self.andOrSearchSolution_DFS()
        elif self.tt.get() == "Recursive AND-OR Tree Search (DFS) -- Non-Deterministic":
            self.andOrSearchSolution_DFS()
        elif self.tt.get() == "BFS No Observation With Beliefs":
            self.bfsNoObservationWithBeliefs()
        elif self.tt.get() == "BFS Partial Observation With Beliefs":
            self.bfsPartialObservationWithBeliefs()
        elif self.tt.get() == "CSP":
            self.cspSolution()
        elif self.tt.get() == "CSP-AC3":
            self.cspSolutionAC3()

    def bfsdfsSolution(self):
        self.stopFlag = False
        q = deque()
        visited = set()

        # Mặc định ô đầu tiên là (0,0)
        if not self.currentChess:
            self.currentChess.append((0, 0))

        initialState = tuple(self.currentChess)
        q.append(initialState)
        visited.add(initialState)
        self.addLog(f"Bắt đầu {self.tt.get()} từ vị trí: {initialState}")

        while q and not self.stopFlag:
            # Chọn state tiếp theo theo thuật toán
            if self.tt.get() == "BFS":
                state = q.popleft()
            elif self.tt.get() == "DFS":
                state = q.pop()

            state = list(state)
            rows = [r for (r, c) in state]
            cols = [c for (r, c) in state]
            self.updateDisplay(state)

            # Kiểm tra có phải goal state
            if len(set(rows)) == 8 and len(set(cols)) == 8 and list(state) == self.currentPositions:
                print("Found solution:", state)
                [print("Visited: ", a) for a in visited]
                self.addLog(f"Found solution: {state}")
                return

            # Sinh trạng thái tiếp theo
            nextCols = [i for i in range(8) if i not in cols]
            nextRows = [i for i in range(8) if i not in rows]
            for i in nextRows:
                for j in nextCols:
                    newList = list(state) + [(i, j)]
                    newList.sort(key=lambda x: x[0]) # sắp xếp list theo hàng
                    newState = tuple(newList)
                    if tuple(newState) not in visited:
                        q.append(newState)
                        visited.add(newState)

            self.root.update()
            time.sleep(self.speed)

        if self.stopFlag == True:
            print("Stopped by user")
            self.addLog("Stopped by user")
        self.addLog(f"No found solution: {state}")

    def inFrontier(self, state, q):
        # Kiểm tra state có trong q không
        for (cost, s) in q:
            if s == state:
                return True
        return False

    def replaceIfBetter(self, state, newPathCost, q):
        # Thay thế state trong q nếu PATH-COST mới tốt hơn
        for i, (cost, s) in enumerate(q):
            if s == state and cost > newPathCost:
                return True
        return False

    def ucsSolution(self):
        self.stopFlag = False

        q = []
        visited = set()

        # Mặc định ô đầu tiên là (0,0)
        if not self.currentChess:
            self.currentChess.append((0, 0))

        start = tuple(self.currentChess)
        pathCost = self.cost(start)
        heapq.heappush(q, (pathCost, start))  # (chi phí, state)
        self.addLog(f"Bắt đầu UCS từ {start} với cost={pathCost}")

        while q and not self.stopFlag:
            # Chọn state tiếp theo theo thuật toán
            # Lấy state có cost nhỏ nhất
            costValue, state = heapq.heappop(q)
            state = list(state)

            self.updateDisplay(state)

            rows = [r for (r, c) in state]
            cols = [c for (r, c) in state]
            # Kiểm tra có phải goal state
            if len(set(rows)) == 8 and len(set(cols)) == 8 and list(state) == self.currentPositions:
                print("---------------------------------------------------------------")
                print("Found solution:", state, costValue, sep=": ")
                [print("Visited: ", a) for a in visited]
                self.addLog(f"found solution: {state}")
                self.addLog(f"Cost: {costValue} | Visited: {len(visited)}")
                break

            # Bỏ qua nếu đã thăm
            if tuple(state) in visited:
                continue
            # Đánh dấu state đã thăm
            visited.add(tuple(state))


            nextCols = [i for i in range(8) if i not in cols]
            nextRows = [i for i in range(8) if i not in rows]
            for i in nextRows:
                for j in nextCols:
                    newList = list(state) + [(i, j)]
                    newList.sort(key=lambda x: x[0])  # sắp xếp list theo hàng
                    newState = tuple(newList)

                    if tuple(newState) not in visited or newState not in self.inFrontier(state, q):
                        newCost = self.cost(newState)
                        newPathCost = costValue + newCost
                        heapq.heappush(q, (newPathCost, newState))

                    # Nếu có trong q với PATH-COST cao hơn thì thay thế
                    elif self.replaceIfBetter(newState, self.cost(newState) + costValue, q):
                        # Xóa state cũ trong q (tìm và xóa chính xác)
                        q_temp = []
                        replaced = False
                        for cost_item, state_item in q:
                            if state_item == newState and cost_item > costValue + self.cost(newState):
                                if not replaced:
                                    q_temp.append((costValue + self.cost(newState), newState))
                                    replaced = True
                            else:
                                q_temp.append((cost_item, state_item))
                        q[:] = q_temp  # Cập nhật lại queue
                        heapq.heapify(q)  # Khôi phục heap property: sắp xếp lại q để đúng theo min-heap

            self.root.update()
            time.sleep(0.05)

        if self.stopFlag == True:
            print("Stopped by user")
            self.addLog("Stopped by user")
        self.addLog(f"No found solution: {state}")

    def dlsSolution(self, limit=8):
        self.stopFlag = False
        visited = set()

        # Mặc định ô đầu tiên là (0,0)
        if not self.currentChess:
            self.currentChess.append((0, 0))
        start = tuple(self.currentChess)

        print(f"Starting DLS with limit: {limit}")
        self.addLog(f"Starting DLS with state {start}, limit {limit}")

        # Gọi hàm đệ quy DLS
        result = self.recursiveDLS(start, visited, limit, 0)

        if result == "cutoff":
            self.addLog(f"Cắt tỉa ở depth {limit} - Thử limit cao hơn")
            print("Search was cut off - try higher limit")
            return None
        elif result == "failure":
            self.addLog(f"No found solution: {result}")
            print("No solution found")
            return None
        else:
            print("---------------------------------------------------------------")
            print("Found solution:", result)
            print("States explored:", len(visited))
            self.addLog(f"Found solution: {result}")
            return result

    def recursiveDLS(self, state, visited, limit, depth):
        if self.stopFlag:
            return "failure"

        # Thêm vào visited để đếm
        visited.add(state)

        self.addLog(f"Depth: {depth}, state: {state}")
        self.updateDisplay(state)
        self.root.update()
        time.sleep(0.05)

        # Kiểm tra goal state
        if len(state) == 8 and self.cost(state) == 0 and list(state) == self.currentPositions:
            return state

        elif limit == 0:
            return "cutoff"

        else:
            cutoffOccurred = False

            rows = [r for (r, c) in state]
            cols = [c for (r, c) in state]
            nextCols = [i for i in range(8) if i not in cols]
            nextRows = [i for i in range(8) if i not in rows]
            for i in nextRows:
                for j in nextCols:
                    newList = list(state) + [(i, j)]
                    newList.sort(key=lambda x: x[0])  # sắp xếp list theo hàng
                    newState = tuple(newList)

                    # Gọi đệ quy
                    result = self.recursiveDLS(newState, visited, limit - 1, depth + 1)


                    if result == "cutoff":
                        cutoffOccurred = True

                    elif result != "failure":
                        return result

            if cutoffOccurred:
                return "cutoff"
            else:
                return "failure"

    def greedySolution(self):
        self.stopFlag = False
        visited = set()
        q = []
        # Mặc định ô đầu tiên là (0,0)
        if not self.currentChess:
            self.currentChess.append((0, 0))
        start = self.currentChess
        hCost = self.costMahattan(start)
        heapq.heappush(q, (hCost, start))  # (chi phí, state)

        while q and not self.stopFlag:
            # Chọn state tiếp theo theo thuật toán
            # Lấy state có cost nhỏ nhất
            costValue, state = heapq.heappop(q)

            self.addLog(f"State {state}, cost: {costValue}")
            self.updateDisplay(state)

            rows = [r for (r, c) in state]
            cols = [c for (r, c) in state]
            # Kiểm tra có phải goal state
            if len(set(rows)) == 8 and len(set(cols)) == 8 and list(state) == self.currentPositions:
                print("---------------------------------------------------------------")
                print("Found solution:", state, costValue, sep=": ")
                [print("Visited: ", a) for a in visited]
                self.addLog(f"Found solution:")
                self.addLog(f"State {state}, cost: {costValue}")
                return

            if tuple(state) in visited:
                continue
            # Đánh dấu state đã thăm
            visited.add(tuple(state))

            # sinh trang thai
            nextCols = [i for i in range(8) if i not in cols]
            nextRows = [i for i in range(8) if i not in rows]
            for i in nextRows:
                for j in nextCols:
                    newList = list(state) + [(i, j)]
                    newList.sort(key=lambda x: x[0])  # sắp xếp list theo hàng
                    newState = tuple(newList)
                    if tuple(newState) not in visited:
                        newCost = self.costMahattan(newState)
                        heapq.heappush(q, (newCost, newState))

            self.root.update()
            time.sleep(0.05)

        if self.stopFlag == True:
            print("Stopped by user")
            self.addLog(f"Stopped by user")
        self.addLog(f"No found solution: {state}")

    def aStarSolution(self):
        self.stopFlag = False
        visited = set()
        q = []

        # Mặc định ô đầu tiên là (0,0)
        if not self.currentChess:
            self.currentChess.append((0, 0))
        start = self.currentChess
        hCost = self.costMahattan(start)
        heapq.heappush(q, (hCost, start))  # (chi phí, state)

        while q and not self.stopFlag:
            # Chọn state tiếp theo theo thuật toán
            # Lấy state có cost nhỏ nhất
            costValue, state = heapq.heappop(q)

            self.addLog(f"State {state}, cost: {costValue}")
            self.updateDisplay(state)

            rows = [r for (r, c) in state]
            cols = [c for (r, c) in state]
            # Kiểm tra có phải goal state
            if len(set(rows)) == 8 and len(set(cols)) == 8 and list(state) == self.currentPositions:
                print("---------------------------------------------------------------")
                print("Found solution:", state, costValue, sep=": ")
                [print("Visited: ", a) for a in visited]
                self.addLog(f"Found solution:")
                self.addLog(f"State {state}, cost: {costValue}")
                return

            # Đánh dấu state đã thăm
            visited.add(tuple(state))

            # sinh trang thai
            nextCols = [i for i in range(8) if i not in cols]
            nextRows = [i for i in range(8) if i not in rows]
            for i in nextRows:
                for j in nextCols:
                    newList = list(state) + [(i, j)]
                    newList.sort(key=lambda x: x[0])  # sắp xếp list theo hàng
                    newState = tuple(newList)
                    if tuple(newState) not in visited:
                        currentCost = self.cost(newState) + costValue
                        newCost = self.costMahattan(newState) + currentCost
                        heapq.heappush(q, (newCost, newState))

            self.root.update()
            time.sleep(0.05)

        if self.stopFlag == True:
            print("Stopped by user")
            self.addLog(f"Stopped by user")
        self.addLog(f"No found solution: {state}")

    def idsSolution(self, maxDepth = 20):
        self.stopFlag = False

        # Mặc định ô đầu tiên là (0,0)
        if not self.currentChess:
            self.currentChess.append((0, 0))
        start = tuple(self.currentChess)

        print(f"Starting DLS with max depth: {maxDepth}")
        self.addLog(f"Starting DLS with max depth: {maxDepth}")
        totalStatesExplored = 0

        # Iterative Deepening: tăng dần limit từ 0
        for depth in range(maxDepth + 1):
            if self.stopFlag:
                break

            print(f"\n--- Trying depth limit: {depth} ---")
            self.addLog(f"Trying depth limit: {depth}")
            visited = set()  # Reset visited cho mỗi lần lặp

            # Gọi DLS với limit hiện tại
            result = self.recursiveDLS(start, visited, depth, 0)
            totalStatesExplored += len(visited)

            print(f"Depth {depth}: States explored = {len(visited)}")
            self.addLog(f"Depth {depth}: States explored = {len(visited)}")

            # Nếu không phải cutoff, trả về kết quả
            if result != "cutoff":
                if result == "failure":
                    print("No solution found at any depth")
                    self.addLog(f"No solution found at any depth")
                    return None
                else:
                    print("---------------------------------------------------------------")
                    print(f"Found solution at depth {depth}:", result)
                    self.addLog(f"Found solution at depth {depth}")
                    print(f"Total states explored across all depths: {totalStatesExplored}")
                    return result

        if self.stopFlag == True:
            print("Stopped by user")
            self.addLog(f"Stopped by user")

        # Nếu đã thử hết tất cả độ sâu
        print("No solution found within max depth limit")
        self.addLog(f"No solution found within max depth limit")
        return None

    def hillClimbing(self):
        self.stopFlag = False

        # Khởi tạo
        if not self.currentChess:
            cols = list(range(8))
            random.shuffle(cols)
            current = [(row, cols[row]) for row in range(8)]
            current.sort(key=lambda x: x[0])
        else:
            current = self.currentChess
        current.sort(key=lambda x: x[0])
        current_cost = self.costChebyshev(current)
        print(f"Initial cost: {current_cost}, state: {current}")
        self.addLog(f"Initial cost: {current_cost}, state: {current}")
        self.updateDisplay(current)

        iteration = 0
        while not self.stopFlag and current_cost > 0:
            # Tìm successor tốt nhất
            best_state, best_cost = self.getBestRookSuccessor(current)

            # Nếu đạt Goal State --> Dừng
            if best_state == self.currentPositions:
                print(f"Found solution: {best_state}")
                self.addLog(f"Found solution: {best_state}")

            # Nếu không tìm được state tốt hơn -> dừng
            if best_cost >= current_cost:
                print(f"Local optimum: {current_cost} conflicts")
                self.addLog(f"Local optimum: {current_cost} conflicts")
                break

            current = best_state
            current_cost = best_cost
            iteration += 1

            self.updateDisplay(current)
            self.root.update()
            time.sleep(0.05)

        if self.stopFlag == True:
            print("Stopped by user")
            self.addLog(f"Stopped by user")

        if current_cost == 0:
            print(f"Solution found: {current}")
            self.addLog(f"Solution found: {current}")
        return current

    def getBestRookSuccessor(self, state):
        current_state = list(state)
        best_cost = self.costChebyshev(current_state)
        best_state = current_state

        # Thử di chuyển từng rook
        for i in range(len(current_state)):
            old_pos = current_state[i]
            occupied = set(current_state) - {old_pos}

            # Thử tất cả vị trí available
            for r in range(8):
                for c in range(8):
                    if (r, c) not in occupied:
                        # Tạo state mới và đánh giá
                        new_state = current_state.copy()
                        new_state[i] = (r, c)
                        cost = self.costChebyshev(new_state)

                        if cost < best_cost:
                            best_cost = cost
                            new_state.sort(key=lambda x: x[0])
                            best_state = tuple(new_state)

        return best_state, best_cost

    def simulatedAnnealing(self):
        self.stopFlag = False

        # Temperature
        def schedule(t):
            initialTemp = 100
            max_iterations = 1000

            if t >= max_iterations:
                return 0

            temp = initialTemp*(0.95**t)
            return max(temp, 0)


        # random state
        if not self.currentChess:
            current = []
            for row in range(8):
                col = random.randint(0, 7)
                current.append((row, col))
        else:
            current = self.currentChess
            while len(current) < 8:
                available_rows = [i for i in range(8) if i not in [r for r, c in current]]
                if available_rows:
                    row = random.choice(available_rows)
                    col = random.randint(0, 7)
                    current.append((row, col))

        current.sort(key=lambda x: x[0])  # row


        # Main loop
        t = 1
        while not self.stopFlag:
            T = schedule(t)

            if T == 0:
                print("Temperature reached 0, terminating...")
                self.addLog(f"Temperature reached 0, terminating...")
                break
            # self.updateDisplay(current)

            # Check goal
            if current == self.bfsPosition:
                print("---------------------------------------------------------------")
                print("Found solution:", current)
                self.addLog(f"Found solution: {current}")
                break

            # Sinh ngau nhiên
            next_state = self.getRandomRookSuccessor(current)

            if next_state is None:
                break

            # Tính (ΔE)
            current_conflicts = self.costChebyshev(current) + self.countRookConflicts(current)
            next_conflicts = self.costChebyshev(next_state) + self.countRookConflicts(next_state)
            delta_E = next_conflicts - current_conflicts


            if delta_E <= 0:
                # Tốt hơn
                current = next_state
            else:
                # Tệ hơn
                probability = math.exp(-delta_E / T)
                if random.random() < probability:
                    current = next_state
                    print(f"Accepted probability {probability:.4f}")
                    self.addLog(f"Accepted probability {probability:.4f}")
            self.updateDisplay(current)
            self.root.update()
            time.sleep(0.02)
            t += 1

            if t > 1000:
                print("Maximum iterations reached")
                self.addLog(f"Maximum iterations reached")
                break

        if self.stopFlag:
            print("Stopped by user")
            self.addLog(f"Stopped by user")

        return current

    def countRookConflicts(self, state):
        # Đếm số cặp rook xung đột: cùng hàng hoặc cùng cột
        if not state:
            return 0

        conflicts = 0
        n = len(state)
        for i in range(n):
            for j in range(i + 1, n):
                r1, c1 = state[i]
                r2, c2 = state[j]

                if r1 == r2 or c1 == c2:
                    conflicts += 1
        return conflicts

    def getRandomRookSuccessor(self, state):
        # Sinh ngẫu nhiên
        if not state:
            return None

        current_state = list(state)

        # Chọn random một rook
        rook_idx = random.randint(0, len(current_state) - 1)
        old_position = current_state[rook_idx]

        # Tìm tất cả vị trí không bị chiếm
        occupied_positions = set(current_state)
        occupied_positions.remove(old_position)

        available_positions = [(r, c) for r in range(8) for c in range(8)
                               if (r, c) not in occupied_positions]

        if not available_positions:
            return None

        # Chọn random vị trí mới
        new_position = random.choice(available_positions)

        # Tạo state mới
        new_state = current_state.copy()
        new_state[rook_idx] = new_position
        new_state.sort(key=lambda x: x[0])

        return new_state

    def beamSearch(self):
        self.stopFlag = False
        currentLevel = []
        visited = set()
        k = 2

        # khởi tạo trạng thái ban đầu
        if not self.currentChess:
            state = []
            for row in range(8):
                state.append((row,0))
            def costM(state):
                r, c = state
                cost = 0
                for i,j in self.currentPositions:
                    if c == j:
                        cost += abs(r - i)
                return cost
            state.sort(key=lambda x: costM(x))
            print(state)

            initialState = []
            initialState.append(state[0])
        else:
            initialState = self.currentChess

        currentLevel.append(tuple(initialState))
        visited.add(tuple(initialState))

        while currentLevel and not self.stopFlag:
            print(f"Current level size: {len(currentLevel)}")
            self.addLog(f"Current level size: {len(currentLevel)}")
            nextLevel = []

            # Xử lý tất cả states trong level hiện tại
            for state in currentLevel:
                print(f"Processing state: {state}")
                self.addLog(f"Processing state: {state}")
                visited.add(tuple(state))
                self.updateDisplay(state)

                # Kiểm tra goal state
                if list(state) == self.currentPositions:
                    print("Found solution:", state)
                    self.addLog(f"Found solution: {state}")
                    return

                # Sinh trạng thái tiếp theo
                rows = [r for (r, c) in state]
                cols = [c for (r, c) in state]

                for i in range(8):
                    for j in range(8):
                        if i not in rows and j not in cols:
                            newList = list(state) + [(i, j)]
                            newState = tuple(newList)
                            if tuple(newState) not in visited:
                                nextLevel.append(newState)
                                print(f"Added new state: {newState} : {self.costChebyshev(newState)}")
                                self.addLog(f"Added new state: {newState}")

            # Chọn k states tốt nhất cho level tiếp theo
            if nextLevel:
                nextLevel.sort(key=lambda x: self.costChebyshev(x))
                currentLevel = nextLevel[:k]  # Chỉ giữ k states tốt nhất
                print(f"Selected {len(currentLevel)} best states for next level")
                self.addLog(f"Selected {len(currentLevel)} best states for next level")
            else:
                print("No solution found")
                self.addLog(f"No solution found")
                break

            self.root.update()
            time.sleep(0.05)

        if self.stopFlag:
            print("Stopped by user")
            self.addLog(f"Stopped by user")

    def geneticAlgorithm(self, maxGenerations=100, populationSize=10, mutationRate=0.2):
        self.stopFlag = False
        population = []

        # Khởi tạo quần thể ban đầu
        for _ in range(populationSize):
            cols = list(range(8))
            random.shuffle(cols)
            current = [(row, cols[row]) for row in range(8)]
            current.sort(key=lambda x: x[0])  # sort row
            cost = self.fitness(current)
            heapq.heappush(population, (cost, current))

        generation = 0
        bestCost, bestState = population[0]
        print(f"Gen {generation} - Best fitness: {bestCost}, {bestState}")
        self.addLog(f"Gen {generation} - Best fitness: {bestCost}, {bestState}")
        self.updateDisplay(bestState)

        # Loop
        while generation < maxGenerations and not self.stopFlag:
            generation += 1

            # Chọn cha mẹ (lấy 2 cá thể tốt nhất)
            p1_cost, p1 = heapq.heappop(population)
            p2_cost, p2 = heapq.heappop(population)

            # Sinh 2 con
            children = self.crossover(p1, p2)

            newPopulation = []
            for child in children:
                # Mutate
                if random.random() < mutationRate:
                    child = self.mutate(child)

                # Đánh giá fitness
                cost = self.fitness(child)
                newPopulation.append((cost, child))

                # Kiểm tra goal state
                if child == self.currentPositions:
                    print("Found solution at generation", generation, ":", child)
                    self.addLog(f"Found solution at generation {generation}: {child}")
                    self.updateDisplay(bestState)
                    return

            # Gộp lại population (giữ cha mẹ + con)
            population.extend(newPopulation)
            heapq.heapify(population)

            # Giữ lại top k tốt nhất
            population = heapq.nsmallest(populationSize, population)

            # Theo dõi kết quả
            bestCost, bestState = population[0]
            print(f"Gen {generation} - Best fitness: {bestCost}, {bestState}")
            self.addLog(f"Gen {generation} - Best fitness: {bestCost}, {bestState}")
            self.updateDisplay(bestState)
            self.root.update()
            time.sleep(0.005)

        print("No solution found. Best state:", bestState, "with cost:", bestCost)
        self.addLog(f"No solution found. Best state: {bestState}")
        self.root.update()
        time.sleep(0.005)

    def fitness(self, state):
        # Đếm số cặp rook xung đột: cùng hàng hoặc cùng cột
        conflicts = self.countRookConflicts(state)
        # Tính khoảng cách tới goal state
        #costValue = self.costMahattan(state)
        costValue = self.costChebyshev(state)
        return costValue + conflicts

    def crossover(self, p1, p2):
        n = len(p1) // 2  # 4
        q = []

        # Sinh 2 con
        p1_left, p1_right = p1[:n], p1[n:]
        p2_left, p2_right = p2[:n], p2[n:]
        child1 = p1_left + p2_right   # trái + phải
        child2 = p2_left + p1_right   # phải + trái

        q.append(child1)
        q.append(child2)
        return q

    def mutate(self, state):
        newState = list(state)
        i, j = random.sample(range(8), 2)
        # hoán đổi cột giữa 2 hàng
        newState[i], newState[j] = (newState[i][0], newState[j][1]), (newState[j][0], newState[i][1])
        newState.sort(key=lambda x: x[0])
        return newState

    def andOrSearchSolution_DFS(self):
        self.stopFlag = False
        self.visited = set()

        # Mặc định bàn cờ trống
        initialState = tuple([])
        result = self.orSearch(initialState, [])

        if result != "failure":
            print("Found solution:", result)
            print("Total visited states:", len(self.visited))
            self.addLog(f"Found solution: {result}")
            return result
        else:
            print("No solution found")
            self.addLog(f"No solution found: {result}")
            print("Total visited states:", len(self.visited))
            print("Path", result)
            return None

    def orSearch(self, state, path):
        # Ít nhất một hành động thành công
        if self.stopFlag:
            return "failure"

        # Cập nhật display
        print("State: ", state)
        self.addLog(f"State: {state}")
        self.updateDisplay(list(state))
        self.root.update()
        time.sleep(0.1)

        # Kiểm tra goal state
        if self.isGoalState(state):
            print("Goal state found", state)
            self.addLog(f"Goal state found: {state}")
            return []  # empty plan - đã đạt mục tiêu

        # Kiểm tra có chu trình (cycle) không
        if state in path:
            print("Cycle detected", state)
            self.addLog(f"Cycle detected: {state}")
            return "failure"


        # Thử tất cả các hành động có thể
        actions = self.getActions(state)

        for action in actions:
            if self.stopFlag:
                return "failure"

            # Thực hiện hành động và lấy tất cả kết quả có thể
            if self.tt.get == "Recursive AND-OR Tree Search (DFS)":
                resultStates = self.getResults(state, action)
            else:
                resultStates = self.getNonDeterministicResults(state, action)

            # AND-SEARCH cho tất cả kết quả có thể của hành động này
            plan = self.andSearch(resultStates, path + [state])

            if plan != "failure":
                return [action] + (plan if isinstance(plan, list) else [])

        return "failure"

    def andSearch(self, states, path):
        # Tất cả các state phải thành công
        if self.stopFlag:
            return "failure"

        plans = []

        # Mỗi state trong states phải có plan thành công
        for i, state in enumerate(states):
            plan_i = self.orSearch(state, path)
            if plan_i == "failure":
                return "failure"  # Nếu bất kỳ state nào fail thì toàn bộ fail
            plans.append((state, plan_i))

        # Trả về conditional plan
        if len(plans) == 1:
            return plans[0][1]
        else:
            # Tạo conditional plan cho nhiều states
            return self.createConditionalPlan(plans)

    def isGoalState(self, state):
        if len(state) != 8:
            return False

        rows = [r for (r, c) in state]
        cols = [c for (r, c) in state]

        # Kiểm tra 8 quân cờ ở 8 hàng và 8 cột khác nhau
        if len(set(rows)) == 8 and len(set(cols)) == 8:
            # Kiểm tra ma trận goal
            self.currentPositions.sort(key=lambda x: x[0])
            if (list(state) == self.currentPositions):
                return True
        return False

    def getActions(self, state):
        #Lấy tất cả các hành động có thể từ state hiện tại
        if len(state) >= 8:
            return []  # Đã đủ 8 quân

        current_rows = {r for (r, c) in state}
        current_cols = {c for (r, c) in state}

        actions = []
        # Tìm các vị trí có thể đặt quân xe tiếp theo
        for r in range(8):
            if r not in current_rows:
                for c in range(8):
                    if c not in current_cols:
                        actions.append((r, c))
                break # lấy hàng đầu tiên phù hợp

        return actions

    def isSafePosition(self, state, new_pos):
        r_new, c_new = new_pos
        for r, c in state:
            if r == r_new or c == c_new:
                return False
        return True

    def getResults(self, state, action):
        # Lấy tất cả kết quả có thể sau khi thực hiện hành động
        newState = tuple(sorted(list(state) + [action], key=lambda x: x[0]))
        self.visited.add(newState)
        return [newState]

    # TH: nhiều outcome
    def getNonDeterministicResults(self, state, action):
        """
        Tạo multiple outcomes cho một action (non-deterministic)
        Lựa chọn 1: Đặt đúng vị trí như dự định
        Lựa chọn 2: Trượt xuống 1 hàng cùng cột (nếu không phải hàng cuối)
        """
        r, c = action

        # Outcome 1: Đặt đúng vị trí như dự định
        primary_state = tuple(sorted(list(state) + [action], key=lambda x: x[0]))
        results = [primary_state]

        # Outcome 2: Trượt xuống 1 hàng (nếu không phải hàng cuối cùng)
        if r < 7:  # Không phải hàng cuối cùng
            slide_position = (r + 1, c)

            slide_state = tuple(sorted(list(state) + [slide_position], key=lambda x: x[0]))
            results.append(slide_state)

            print(f"Action {action} có thể dẫn đến:")
            print(f"  - Outcome 1: Đặt tại {action}")
            print(f"  - Outcome 2: Trượt xuống {slide_position}")
            self.addLog(f"Action {action} có thể dẫn đến:")
            self.addLog(f"  - Outcome 1: Đặt tại {action}")
            self.addLog(f"  - Outcome 2: Trượt xuống {slide_position}")

        else:
            print(f"Action {action} - hàng cuối, không có lựa chọn trượt")
            self.addLog(f"Action {action} - hàng cuối, không có lựa chọn trượt")

        return results

    def createConditionalPlan(self, plans):
        # Đơn giản hóa: trả về plan đầu tiên
        return plans[0][1] if plans else []

    def bfsNoObservationWithBeliefs(self):
        # No observation --> ko nhìn thấy
        self.stopFlag = False
        queue = deque()
        visited = set()

        # Initial state
        states = []
        for _ in range(5):
            i = random.randint(0, 7)
            state = ((i, i),)   # state: tuple gồm 1 cặp (i,i)
            states.append(state)

        initialBelief = frozenset(states)
        queue.append((initialBelief,[]))
        visited.add(initialBelief)
        print(f"Initial belief with {len(initialBelief)} states:")
        self.addLog(f"Initial belief with {len(initialBelief)} states:")
        for s in initialBelief:
            print("   ", s)

        while queue and not self.stopFlag:
            currentBelief, actionHistory = queue.popleft()

            print(f"Belief state with {len(currentBelief)} possibilities")
            self.addLog(f"Belief state with {len(currentBelief)} possibilities")

            # Update display
            for currentState in currentBelief:
                self.updateDisplay(list(currentState))
                self.root.update()
                time.sleep(0.001)

            # Check goal
            if all(self.isGoalBelief(possibleState) for possibleState in currentBelief):
                print("GOAL REACHED")
                print(f"Goal belief: {currentBelief}")
                print(f"Action sequence: {actionHistory}")
                self.addLog(f"Goal belief: {currentBelief}")
                self.addLog(f"Action sequence: {actionHistory}")
                return actionHistory

            # Sinh tất cả các hành động (no observation)
            all_actions = set()
            for possibleState in currentBelief:
                actions = self.getAllPossibleActions(possibleState)
                all_actions.update(actions)

            # Thực hiện hành động
            for action in all_actions:
                if self.stopFlag:
                    break

                newBelief = set()

                for possibleState in currentBelief:
                    newState = self.executeActionBlindly(possibleState, action)
                    if newState:
                        newBelief.add(newState)

                if newBelief:
                    newBeliefFrozen = frozenset(newBelief)

                    if newBeliefFrozen not in visited:
                        visited.add(newBeliefFrozen)
                        newActionHistory = actionHistory + [action]
                        queue.append((newBeliefFrozen, newActionHistory))

                        print(f"   Action: {action} → belief size: {len(newBelief)}")
                        self.addLog(f"   Action: {action} → belief size: {len(newBelief)}")
                        '''print("   Current belief states:")
                        for s in currentBelief:
                            print(f"      {s}")'''

                        print("   Resulting new states:")
                        self.addLog(f"Resulting belief states")
                        for s in newBelief:
                            print(f"      {s}")
                            self.addLog(f"    {s}")

        if self.stopFlag == True:
            print("Stopped by user")
            self.addLog(f"Stopped by user")

        print("No solution found with belief states")
        self.addLog(f"No solution found with belief states")
        return None

    def bfsPartialObservationWithBeliefs(self):
        # Partial observation --> nhìn thấy 1 phần
        self.stopFlag = False
        queue = deque()
        visited = set()

        # Initial state
        states = []
        states.append(tuple(self.currentPositions))
        row = [r for r,c in self.currentPositions]
        col = [c for r,c in self.currentPositions]

        pos = []
        for i in range(8):
            if i not in row:
                for j in range(8):
                    if j not in col:
                        pos.append((i, j))
        for x in pos:
            state = list(self.currentPositions)
            state.append(x)
            states.append(tuple(state))


        initialBelief = frozenset(states)
        queue.append((initialBelief,[]))
        visited.add(initialBelief)
        print(f"Initial belief with {len(initialBelief)} states:")
        self.addLog(f"Initial belief with {len(initialBelief)} states:")
        for s in initialBelief:
            print("   ", s)

        while queue and not self.stopFlag:
            currentBelief, actionHistory = queue.popleft()

            print(f"Belief state with {len(currentBelief)} possibilities")
            self.addLog(f"Belief state with {len(currentBelief)} possibilities")

            # Update display
            for currentState in currentBelief:
                self.updateDisplay(list(currentState))
                self.root.update()
                time.sleep(0.001)

            # Check goal
            if all(self.isGoalBelief2(possibleState) for possibleState in currentBelief):
                print("GOAL REACHED")
                print(f"Goal belief: {currentBelief}")
                print(f"Action sequence: {actionHistory}")
                self.addLog(f"Goal belief: {currentBelief}")
                self.addLog(f"Action sequence: {actionHistory}")
                return actionHistory

            # Sinh tất cả các hành động
            all_actions = self.getAllPossibleBeliefActions(currentBelief)

            # Thực hiện hành động
            for action in all_actions:
                if self.stopFlag:
                    break

                newBelief = self.executeActionBlindly2(currentBelief, action)
                if newBelief and newBelief not in visited:
                    visited.add(newBelief)
                    newActionHistory = actionHistory + [action[0]]
                    queue.append((newBelief, newActionHistory))

                    print(f"   Action: {action[0]} → belief size: {len(newBelief)}")
                    self.addLog(f"   Action: {action[0]} → belief size: {len(newBelief)}")
                    self.addLog(f"Belief:")
                    for s in newBelief:
                        print(f"      {s}")
                        self.addLog(f"    {s}")
        if self.stopFlag == True:
            print("Stopped by user")
            self.addLog(f"Stopped by user")

        print("No solution found with belief states")
        self.addLog(f"No solution found with belief states")
        return None

    def isGoalBelief(self, state):
        if len(state) != 8:
            return False

        rows = [r for (r, c) in state]
        cols = [c for (r, c) in state]

        # Kiểm tra 8 quân cờ ở 8 hàng và 8 cột khác nhau
        if len(set(rows)) == 8 and len(set(cols)) == 8:
            return True

        return False

    def isGoalBelief2(self, state):
        if len(state) != 8:
            return False

        rows = [r for (r, c) in state]
        cols = [c for (r, c) in state]

        if (not self.currentPositions):
            for x in self.currentPositions:
                if x not in state:
                    return False

        # Kiểm tra 8 quân cờ ở 8 hàng và 8 cột khác nhau
        if len(set(rows)) == 8 and len(set(cols)) == 8:
            return True

        return False

    def getAllPossibleActions(self, currentPieces):
        """
        Actions:
        1. PLACE: Đặt quân mới ở vị trí (r, c)
        2. MOVE: Di chuyển quân từ (r1, c1) đến (r2, c2)
        Return 1 action Place và 1 action Move
        """
        actions = []

        # ACTION 1: PLACE - chỉ lấy 1 action đầu tiên
        if len(currentPieces) < 8:
            rows = {r for (r, c) in currentPieces}
            cols = {c for (r, c) in currentPieces}
            
            found = False
            for r in range(8):
                if r not in rows:
                    for c in range(8):
                        if c not in cols:
                            # Kiểm tra position hợp lệ (không bị tấn công)
                            if self.isValidPlacement(currentPieces, (r, c)):
                                actions.append(('PLACE', (r, c)))
                                found = True
                                break
                    if found:
                        break # lấy hàng đầu tiên hợp lệ

        # ACTION 2: MOVE - chỉ lấy 1 action đầu tiên
        moveFound = False
        for piece_pos in currentPieces:
            if (self.tt.get() == "BFS Partial Observation With Beliefs"):
                # Không di chuyển quân mục tiêu nhìn thấy được 1 phần
                if (piece_pos in self.currentPositions):
                    continue

            # Thử di chuyển đến tất cả positions khác
            for to_r in range(8):
                for to_c in range(8):
                    to_pos = (to_r, to_c)

                    # Không di chuyển đến chỗ cũ hoặc chỗ đã có quân khác
                    if (to_pos != piece_pos and
                            to_pos not in currentPieces and
                            self.isValidMove(currentPieces, piece_pos, to_pos)):
                        actions.append(('MOVE', piece_pos, to_pos))
                        moveFound = True
                        break
                if moveFound:
                    break
            if moveFound:
                break
            

        return actions

    def getAllPossibleBeliefActions(self, currentBelief):
        """
        Sinh 2 loại action cho belief:
        1. PLACE: mỗi state trong belief thử place thêm quân -> tập belief mới
            - Mỗi state tìm 1 vị trí place riêng
            - Nếu state nào không place được thì bỏ qua
        2. MOVE: mỗi state trong belief thử move quân -> tập belief mới
            - Mỗi state tìm 1 vị trí move riêng
            - Không move nếu state đã đạt goal
        """
        actions = []

        # ACTION 1: PLACE
        placeBelief = set()
        for state in currentBelief:
            found = False
            if len(state) < 8:
                rows = {r for (r, c) in state}
                cols = {c for (r, c) in state}
                for r in range(8):
                    if r not in rows:
                        for c in range(8):
                            if c not in cols and self.isValidPlacement(state, (r, c)):
                                newState = tuple(sorted(list(state) + [(r, c)]))
                                placeBelief.add(newState)
                                found = True
                                break
                        if found:
                            break 
        if placeBelief:
            actions.append(("PLACE", frozenset(placeBelief)))

        # ACTION 2: MOVE
        moveBelief = set()
        for state in currentBelief:
            # Không move nếu state đã đạt goal
            if self.isGoalBelief2(state):
                continue
            moveFound = False
            for from_pos in state:
                if from_pos in self.currentPositions:  # không move quân nhìn thấy
                    continue

                from_r, from_c = from_pos
                for to_r in range(8):
                    for to_c in range(8):
                        to_pos = (to_r, to_c)
                        if (to_pos != from_pos and
                                to_pos not in state and
                                self.isValidMove(state, from_pos, to_pos)):
                            newStateList = list(state)
                            newStateList.remove(from_pos)
                            newStateList.append(to_pos)
                            newState = tuple(sorted(newStateList))
                            moveBelief.add(newState)
                            moveFound = True
                            break
                    if moveFound:
                        break
        if moveBelief:
            actions.append(("MOVE", frozenset(moveBelief)))

        return actions

    def isValidPlacement(self, current_pieces, new_pos):
        # Kiểm tra vị trí đặt quân mới có hợp lệ không
        new_r, new_c = new_pos

        # Kiểm tra không trùng vị trí
        if new_pos in current_pieces:
            return False

        # Kiểm tra không bị tấn công bởi quân hiện tại
        for r, c in current_pieces:
            if r == new_r or c == new_c:
                return False

        return True

    def isValidMove(self, current_pieces, from_pos, to_pos):
        # Kiểm tra việc di chuyển quân có hợp lệ không

        new_pieces = list(current_pieces)
        new_pieces.remove(from_pos)
        new_pieces.append(to_pos)

        # Kiểm tra state mới có hợp lệ không
        return self.isValidState(tuple(new_pieces))

    def executeActionBlindly(self, current_pieces, action):
        """
        Thực hiện action mà không nhìn thấy kết quả

        Trong thực tế: Agent không biết kết quả
        Trong simulation: Chúng ta cần biết để tiếp tục search
        """
        action_type = action[0]

        try:
            if action_type == 'PLACE':
                _, new_pos = action
                # Nếu new_pos đã có trong state thì bỏ qua
                if new_pos in current_pieces:
                    return None
                new_pieces = tuple(sorted(list(current_pieces) + [new_pos]))
                return new_pieces

            elif action_type == 'MOVE':
                _, from_pos, to_pos = action
                # Chỉ move nếu from_pos đang tồn tại trong state
                if from_pos not in current_pieces:
                    return None
                new_pieces_list = list(current_pieces)
                new_pieces_list.remove(from_pos)
                new_pieces_list.append(to_pos)
                new_pieces = tuple(sorted(new_pieces_list))
                return new_pieces

            else:
                print(f"Unknown action type: {action_type}")
                return None

        except Exception as e:
            print(f"Error executing action {action}: {e}")
            return None

    def executeActionBlindly2(self, currentBelief, action):
        """
        Thực hiện action trên belief:
        Trả về belief mới (frozenset states)
        """
        try:
            action_type, newBelief = action
            if not newBelief:
                return None
            return newBelief
        except Exception as e:
            print(f"Error executing action {action}: {e}")
            return None

    def isValidState(self, pieces):
        # Kiểm tra state có hợp lệ không
        if not pieces:
            return True

        rows = [r for (r, c) in pieces]
        cols = [c for (r, c) in pieces]

        # Kiểm tra không có 2 quân cùng hàng hoặc cùng cột
        if len(set(rows)) != len(rows) or len(set(cols)) != len(cols):
            return False

        # Kiểm tra trong boundary
        for r, c in pieces:
            if r < 0 or r >= 8 or c < 0 or c >= 8:
                return False

        return True

    def cspSolution(self):
        self.stopFlag = False
        # Khởi tạo
        pos = [(None,None)] * 8 # [(None,None), (None,None), (None,None), (None,None), (None,None), (None,None), (None,None), (None,None)]
        values = [(i, j) for i in range(8) for j in range(8)]
        visited = []
        n = [0, 1, 2, 3, 4, 5, 6, 7]

        # ràng buộc bt 8 Rook
        def constraint(pos, x):
            if pos is None:
                return True

            if x in pos:
                return False

            rx, cx = x
            if rx not in range(8) and cx not in range(8):
                return False

            for r, c in pos:
                if (r, c) != (None, None):
                    if r == rx or c == cx:
                        return False
            return True

        def constraintQueens(pos, x):
            if x is None:
                return True
            rx, cx = x

            if rx not in range(8) or cx not in range(8):
                return False

            for r, c in pos:
                if (r, c) != (None, None):

                    if r == rx or c == cx:
                        return False
                    #
                    if abs(r - rx) == abs(c - cx):
                        return False
            return True

        # Forward checking
        def forwardCheck(values, x):
            rx, cx = x
            newValues = []
            return [(r, c) for (r, c) in values if r != rx and c != cx]

        def forwardCheckQueens(values, x):
            rx, cx = x
            newValues = []
            return [(r, c) for (r, c) in values if r != rx and c != cx and abs(r - rx) != abs(c - cx)]

        # Loop
        while n and not self.stopFlag:
            i = random.choice(n) # Chọn biến
            n.remove(i)
            visited.append(i)
            v = values.copy()
            selected = False
            while v:
                value = random.choice(v) # Chọn giá trị cho biến
                # Kiểm tra ràng buộc
                if constraint(pos,value):
                    pos[i] = value
                    v = forwardCheck(values, value)
                    visited.append(i)
                    selected = True
                    break
                else:
                    v.remove(value)

            print(f"Position {i}: {value}")
            self.addLog(f"Position {i}: {value}")
            self.updateDisplay(pos)
            self.root.update()
            time.sleep(0.001)

            if not selected:
                # backtracking
                if not visited:
                    print("No found Solution")
                    self.addLog("No found Solution")
                    return None

                t = visited.pop()
                pos[t] = (None,None)
                if t not in n:
                    n.append(t)

        if self.stopFlag == True:
            print("Stopped by user")
            self.addLog(f"Stopped by user")

        print(f"Found Solution: {pos}")
        self.addLog(f"Found Solution: {pos}")

    def cspSolutionAC3(self):
        self.stopFlag = False

        # Khởi tạo domain cho mỗi biến (8 quân rook)
        domains = {i: [(r, c) for r in range(8) for c in range(8)] for i in range(8)}
        pos = [(None, None)] * 8

        # Kiểm tra ràng buộc giữa 2 giá trị
        def constraint_two_vars(val_i, val_j):
            if val_i == (None, None) or val_j == (None, None):
                return True
            ri, ci = val_i
            rj, cj = val_j
            return ri != rj and ci != cj

        # Hàm AC-3 độc lập
        def ac3(domains):
            # Tạo danh sách các cung (arcs)
            queue = [(i, j) for i in range(8) for j in range(8) if i != j]

            while queue and not self.stopFlag:
                xi, xj = queue.pop(0)

                if revise(domains, xi, xj):
                    # Nếu domain rỗng, không có solution
                    if len(domains[xi]) == 0:
                        return False

                    # Thêm tất cả các cung (xk, xi) vào queue (trừ xj)
                    for xk in range(8):
                        if xk != xi and xk != xj:
                            queue.append((xk, xi))

            return True

        # Revise function - loại bỏ giá trị không nhất quán
        def revise(domains, xi, xj):
            revised = False
            to_remove = []

            for val_i in domains[xi]:
                # Kiểm tra xem có tồn tại giá trị nào trong domain của xj
                # thỏa mãn ràng buộc với val_i không
                has_support = any(constraint_two_vars(val_i, val_j)
                                  for val_j in domains[xj])

                # Nếu không có giá trị nào hỗ trợ, loại bỏ val_i
                if not has_support:
                    to_remove.append(val_i)
                    revised = True

            # Loại bỏ các giá trị không nhất quán
            for val in to_remove:
                domains[xi].remove(val)

            return revised

        # Backtracking với domain đã thu hẹp
        def backtrack(assignment, remaining_vars):
            if self.stopFlag:
                return None

            if not remaining_vars:
                return assignment

            # Chọn biến với domain nhỏ nhất (MRV heuristic)
            var = min(remaining_vars, key=lambda x: len(domains[x]))
            remaining_vars.remove(var)

            for value in domains[var][:]:
                # Kiểm tra ràng buộc với các biến đã gán
                if all(constraint_two_vars(value, assignment[i])
                       for i in range(8) if assignment[i] != (None, None)):

                    assignment[var] = value

                    # Hiển thị
                    print(f"Position {var}: {value}")
                    self.addLog(f"Position {var}: {value}")
                    self.updateDisplay(assignment)
                    self.root.update()
                    time.sleep(0.001)

                    result = backtrack(assignment, remaining_vars[:])
                    if result is not None:
                        return result

                    assignment[var] = (None, None)

            remaining_vars.append(var)
            return None

        # Chạy AC-3
        print("Đang chạy AC-3 để thu hẹp domain...")
        self.addLog(f"Đang chạy AC-3 để thu hẹp domain...")
        if not ac3(domains):
            print("Không tìm thấy solution - Domain rỗng sau AC-3!")
            self.addLog(f"Không tìm thấy solution - Domain rỗng sau AC-3!")
            return None

        print(f"AC-3 hoàn tất. Domain đã thu hẹp.")
        self.addLog(f"AC-3 hoàn tất. Domain đã thu hẹp.")
        for i in range(8):
            print(f"Biến {i}: {len(domains[i])} giá trị còn lại")
            self.addLog(f"Biến {i}: {len(domains[i])} giá trị còn lại")

        if self.stopFlag == True:
            print("Stopped by user")
            self.addLog(f"Stopped by user")

        # Tìm solution bằng backtracking
        print("\nBắt đầu tìm kiếm solution...")
        self.addLog(f"Backtracking tìm solution...")
        solution = backtrack(pos, list(range(8)))

        if solution:
            print(f"Found Solution: {solution}")
            self.addLog(f"Found Solution: {solution}")
            return solution
        else:
            print("Không tìm thấy solution!")
            self.addLog(f"No found Solution!")
            return None

    def repairState(self, state):
        """
        Sửa state để đảm bảo mỗi hàng chỉ có 1 cột duy nhất.
        Nếu bị trùng cột thì thay bằng cột còn thiếu.
        """
        rows = [r for r, c in state]
        cols = [c for r, c in state]

        missing_cols = list(set(range(8)) - set(cols))
        random.shuffle(missing_cols)

        seen = set()
        new_state = []

        for (r, c) in state:
            if c in seen:
                # Nếu cột bị trùng, thay bằng cột còn thiếu
                new_c = missing_cols.pop()
                new_state.append((r, new_c))
            else:
                new_state.append((r, c))
                seen.add(c)

        new_state.sort(key=lambda x: x[0])  # sắp xếp lại theo hàng
        return new_state

    def updateDisplay(self, state):
        # Clear bàn cờ trái
        for (r, c) in self.currentChess:
            if r is not None and c is not None:
                self.leftButton[r][c].configure(text=' ', fg='black')
        # Cập nhật lại bàn cờ trái
        self.currentChess = [(r, c) for r, c in state if r is not None and c is not None]
        for (r, c) in self.currentChess:
            self.leftButton[r][c].configure(text='♜', fg='red')

    def isSafe(self, state):
        # Kiểm tra vị trí an toàn
        for (r, c) in state:
            if (c == next_col or
                    abs(r - next_row) == abs(c - next_col)):
                return False
        return True

    def run(self):
        self.root.mainloop()


# Chạy ứng dụng
if __name__ == "__main__":
    app = ChessSolver()
    app.run()
