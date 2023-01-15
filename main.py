import streamlit as st
import sqlite3

DB_PATH = "./task_manegement.db"


# テーブルを作成する関数
def create_table(db_path):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS name_list(name_id integer primary key autoincrement, name text)")
    cur.execute("CREATE TABLE IF NOT EXISTS task_list(task_id integer primary key autoincrement, task_title text, task_detail text, name_id1 integer, name_id2, integer, name_id3 integer, name_id4 integer)")
    con.commit()
    con.close()


# テーブルを削除する関数
def delete_table(db_path):
    con = sqlite3.connect(db_path)
    con.execute("drop table if exists name_list")
    con.execute("drop table if exists task_list")
    con.close()


# task_targetを名前からidに変換する関数
def conversion_name2id(db_path, task_target):
    id_list = []
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    for i in range(len(task_target)):
        if task_target[i] is not None:
            cur.execute("select name_id from name_list where name = \'" + task_target[i] + "\'")
            for j in cur:
                id_list.append(j[0])
    con.commit()
    con.close()
    return id_list

# task_targetをidから名前に変換する関数
def conversion_id2name(db_path, id_list):
    name_list = []
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    for i in range(len(id_list)):
        if id_list[i] is not None:
            cur.execute("select name from name_list where name_id = \'" + str(id_list[i]) + "\'")
            for j in cur:
                name_list.append(j[0])
    con.commit()
    con.close()
    return name_list


# Markdownでタスクを一覧表示する関数
def display_tasklist(db_path):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    sql = "select * from task_list"
    cur.execute(sql)
    data = []
    data = cur.fetchall()

    if data is not None:
        for i in range(len(data)):
            id_list = []
            with st.expander(data[i][1]):
                st.markdown("**タスクID** : " + str(data[i][0]))
                st.markdown("**タスク内容** : " + str(data[i][2]))
                target_sentence = "**タスクの対象者** : "
                for j in range(4):
                    if data[i][j+3] is not None:
                        id_list.append(data[i][j+3])
                name_list = conversion_id2name(DB_PATH, id_list)
                for j in range(len(name_list)):
                    target_sentence = target_sentence + str(name_list[j]) + "&emsp;"
                st.markdown(target_sentence)
    else:
        st.error("未達成タスクがありません")

    con.commit()
    con.close()


# task_listに新規レコードを追加する関数
def add_task_record(db_path, task_title, task_detail, id_list):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    data = [task_title, task_detail]
    for i in id_list:
        data.append(i)
    data = tuple(data)

    if len(id_list) == 1:
        sql = "insert into task_list (task_title, task_detail, name_id1) values (?, ?, ?)"
        cur.execute(sql, data)
    elif len(id_list) == 2:
        sql = "insert into task_list (task_title, task_detail, name_id1, name_id2) values (?, ?, ?, ?)"
        cur.execute(sql, data)
    elif len(id_list) == 3:
        sql = "insert into task_list (task_title, task_detail, name_id1, name_id2, name_id3) values (?, ?, ?, ?, ?)"
        cur.execute(sql, data)
    elif len(id_list) == 4:
        sql = "insert into task_list (task_title, task_detail, name_id1, name_id2, name_id3, name_id4) values (?, ?, ?, ?, ?, ?)"
        cur.execute(sql, data)

    con.commit()
    con.close()


# name_listに新規レコードを追加する関数
def add_name_record(db_path, name):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    sql = "insert into name_list (name) values (?)"
    data = [name]
    cur.execute(sql, data)
    con.commit()
    con.close()


if "number" not in st.session_state:
    st.session_state.number = 0

st.session_state.names = []
if "names" not in st.session_state:
    st.session_state.names = 0

create_table(DB_PATH)

# Title

st.title("Group Task Management App")
st.caption("グループのメンバーを登録し、メンバーに与えるタスクを入力してください")

# Sidebar

st.session_state.number = st.sidebar.selectbox('グループの人数を入力してください', [1, 2, 3, 4])

with st.sidebar.expander("グループ全員の名前を入力してください"):
    for i in range(st.session_state.number):
        name = st.sidebar.text_input(str(i+1) + "人目の名前を入力してください", key=i)
        st.session_state.names.append(name)

if st.sidebar.button("メンバーを登録する"):
    for i in range(len(st.session_state.names)):
        if st.session_state.names[i] is not None:
            add_name_record(DB_PATH, st.session_state.names[i])
    st.sidebar.success("データベースにメンバー情報を追加しました")

if st.sidebar.button("データベースを初期化する"):
    delete_table(DB_PATH)
    create_table(DB_PATH)
    st.sidebar.success("データベースの全テーブルを空にしました")

# Main Page

task_title = st.text_input("タスクのタイトルを入力")
task_detail = st.text_area("タスクの内容を入力")
task_target = st.multiselect("タスクの対象者を選択(複数選択可)", st.session_state.names)

if st.button("タスクを新規追加する"):
    id_list = conversion_name2id(DB_PATH, task_target)
    add_task_record(DB_PATH, task_title, task_detail, id_list)
    st.success("データベースに新規タスクを追加しました")

st.subheader("タスク一覧")
if st.button("タスクを表示する"):
    display_tasklist(DB_PATH)
