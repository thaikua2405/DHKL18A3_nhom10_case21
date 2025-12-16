import pandas as pd

# Đọc dữ liệu 
# File 1: class_schedule 
class_schedule = pd.DataFrame({
    'class_id': ['HP101_01', 'hp101-01', 'HP205_02'],
    'course_name': ['Lap trinh python', 'Lap trinh PY', 'Xac suat thong ke'],
    'weekday': ['Thu 2', 'Mon', 'THÁNG 3'],
    'slot': ['Tiet 1-3', '01-03-2025', 'Ca sang']
})

# File 2: student_class 
student_class = pd.DataFrame({
    'student_id': ['sv001', 'sv002', 'Sv_003', 'sv004'],
    'full_name': ['nguyen van Binh', 'TrAN thi Minh', 'LE quang Huy', 'pham thi Ha'],
    'class_cohort': ['k17a1', 'K17-A1', 'k18a2', 'K18 A2']
})

# File 3: attendance_log 
attendance_log = pd.DataFrame({
    'date': ['01-03-2024', '01-03-2024', '01-03-2024'],
    'class_id': ['hp101-01', 'HP101_01', 'HP205_02'],
    'student_id': ['sv001', 'Sv_003', 'sv002'],
    'status': ['Co mat', 'vang', 'di muon'],
    'note': ['', 'Khong ly do', 'traffic jam']
})

# 1. Chuẩn hóa dữ liệu trước khi merge
print("=== CHUẨN HÓA DỮ LIỆU ===")

# Chuẩn hóa student_id: viết thường, bỏ gạch dưới
student_class['student_id'] = student_class['student_id'].str.lower().str.replace('_', '')
attendance_log['student_id'] = attendance_log['student_id'].str.lower().str.replace('_', '')

# Chuẩn hóa class_id: viết thường, thống nhất định dạng
class_schedule['class_id_norm'] = class_schedule['class_id'].str.lower().str.replace('-', '_')
attendance_log['class_id_norm'] = attendance_log['class_id'].str.lower().str.replace('-', '_')
print("Student IDs sau chuẩn hóa:", student_class['student_id'].unique())
print("Class IDs sau chuẩn hóa:", class_schedule['class_id_norm'].unique())

# 2. Merge student_class với attendance_log theo student_id
print("\n=== MERGE 1: student_class + attendance_log ===")
merged_1 = pd.merge(student_class, attendance_log, 
                    on='student_id', 
                    how='outer',  
                    indicator=True)
print(f"Số dòng sau merge: {len(merged_1)}")
print("\nKiểm tra dữ liệu không khớp:")
print(merged_1['_merge'].value_counts())

# Tìm sinh viên không có trong attendance_log
missing_in_log = merged_1[merged_1['_merge'] == 'left_only']
if not missing_in_log.empty:
    print(f"\nSinh viên không có trong attendance_log: {missing_in_log['student_id'].tolist()}")

# 3. Merge kết quả trên với class_schedule theo class_id
print("\n=== MERGE 2: (student_class + attendance_log) + class_schedule ===")
# Dùng class_id đã chuẩn hóa để merge
merged_final = pd.merge(merged_1, class_schedule,
                        left_on='class_id_norm',
                        right_on='class_id_norm',
                        how='outer',
                        suffixes=('_att', '_class'),
                        indicator='merge2')
print(f"Số dòng sau merge 2: {len(merged_final)}")
print("\nKiểm tra dữ liệu không khớp ở merge 2:")
print(merged_final['merge2'].value_counts())

# 4. Phát hiện vấn đề
print("\n=== PHÁT HIỆN VẤN ĐỀ ===")

# a) Class_id không khớp
class_mismatch = merged_final[merged_final['merge2'] != 'both']
if not class_mismatch.empty:
    print("1. Class_id không khớp hoặc thiếu:")
    print(class_mismatch[['class_id_att', 'class_id_norm']].drop_duplicates())

# b) Sinh viên không có lớp
no_class_students = merged_final[(merged_final['_merge'] == 'both') & 
                                 (merged_final['merge2'] == 'left_only')]
if not no_class_students.empty:
    print("\n2. Sinh viên có điểm danh nhưng không có trong class_schedule:")
    print(no_class_students[['student_id', 'class_id_att']].drop_duplicates())

# c) Lớp không có sinh viên điểm danh
no_attendance_class = merged_final[merged_final['merge2'] == 'right_only']
if not no_attendance_class.empty:
    print("\n3. Lớp trong schedule nhưng không có ai điểm danh:")
    print(no_attendance_class[['class_id_class', 'course_name']].drop_duplicates())

# 5. Tạo file hoàn chỉnh (chỉ giữ dữ liệu hợp lệ)
print("\n=== XUẤT FILE HOÀN CHỈNH ===")
complete_data = merged_final[
    (merged_final['_merge'] == 'both') & 
    (merged_final['merge2'] == 'both')
]

# Chọn và đổi tên cột cần thiết
complete_data = complete_data[[
    'date', 'student_id', 'full_name', 'class_cohort',
    'class_id_class', 'course_name', 'weekday', 'slot',
    'status', 'note'
]].rename(columns={'class_id_class': 'class_id'})

print(f"Số dòng dữ liệu hoàn chỉnh: {len(complete_data)}")
print("\nMẫu dữ liệu hoàn chỉnh:")
print(complete_data.head())

# Xuất file CSV
complete_data.to_csv('complete_attendance_data.csv', index=False, encoding='utf-8-sig')
print("\nĐã xuất file: complete_attendance_data.csv")

# 6. Tóm tắt kết quả
print("\n=== TÓM TẮT ===")
print(f"Tổng sinh viên: {len(student_class)}")
print(f"Tổng lớp học: {len(class_schedule)}")
print(f"Tổng điểm danh: {len(attendance_log)}")
print(f"Dữ liệu hợp lệ sau merge: {len(complete_data)}")
print(f"Dữ liệu không khớp: {len(merged_final) - len(complete_data)}")