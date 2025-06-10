import os

output_path = "integrate.xyz"
input_dir = "./"
prefix = "case_"
suffix = ".xyz"

with open(output_path, "w") as outfile:
    for i in range(1, 101):
        filename = os.path.join(input_dir, f"{prefix}{i:03d}{suffix}")
        if os.path.isfile(filename):
            with open(filename, "r") as infile:
                lines = infile.readlines()
                outfile.writelines(lines)
        else:
            print(f"⚠️ 파일 없음: {filename}")

print(f"✅ 모든 .xyz 파일이 {output_path}로 병합되었습니다.")

