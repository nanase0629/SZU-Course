import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.io.BufferedWriter;
import java.io.FileWriter;

class Student implements Serializable
{
    public int num;
    public String name;
    public String college;
    public int score;
    public Student(int num, String name, String college, int score) {
        this.num = num;
        this.name=name;
        this.college=college;
        this.score=score;
    }
    @Override
    public String toString() {
        return num+" "+name+" "+college+" "+score;
    }
    /*@Override
    public int compareTo(Student o) {
     if(o==null)return 1;
     return this.name.compareTo(o.name);
    }*/
}

public class Main {
    public static List<Student> readStudentsFromFile() {
        List<Student> students = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(new FileReader("data.txt"))) {
            String line = br.readLine();
            while (line != null) {
                String[] strs = line.split(" ");
                int num = Integer.parseInt(strs[0]);
                String name = strs[1];
                String college = strs[2];
                int score = Integer.parseInt(strs[3]);
                Student student = new Student(num, name, college, score);
                students.add(student);
                line = br.readLine();
            }
            students.sort(new Comparator<Student>() {
                @Override
                public int compare(Student o1, Student o2) {
                    return o1.name.compareTo(o2.name);
                }
            });
        } catch (IOException ex) {}
        return students;
    }
    public static void writeStudentsToFile(List<Student> students) {
        try (BufferedWriter bw = new BufferedWriter(new FileWriter("output.txt"))) {
            for (Student student : students) {
                bw.write(student.toString());
                bw.newLine();
            }
        } catch (IOException ex) {}
    }
    public static void printup92(){
        try(BufferedReader br = new BufferedReader(new FileReader("output.txt"))){
            List<Student>students=new ArrayList<>();
            String line = br.readLine();
            while (line!=null){
                String[] strs = line.split(" ");
                int num = Integer.parseInt(strs[0]);
                String name = strs[1];
                String college = strs[2];
                int score = Integer.parseInt(strs[3]);
                if(score<=92){
                    line = br.readLine();
                    continue;
                }
                Student student = new Student(num, name, college, score);
                students.add(student);
                line = br.readLine();
            }
            students.sort(new Comparator<Student>() {
                @Override
                public int compare(Student o1, Student o2) {
                    if(o1.score-o2.score==0)return o2.name.compareTo(o1.name);
                    return o2.score-o1.score;
                }
            });
            for(Student student:students){
                System.out.println(student);
            }
        }
        catch (IOException ex){}

    }
    public static void main(String[] args) {
        List<Student>students= readStudentsFromFile();
        writeStudentsToFile(students);
        printup92();
    }
}