import java.util.Scanner;
interface Comparable<T>{
    int compareTo(T others);
}
abstract class GeometricObject implements Comparable<GeometricObject>{
    abstract double getArea();
    public int compareTo(GeometricObject g) {
        if(this.getArea() > g.getArea())return 1;
        else if(this.getArea() < g.getArea())return -1;
        else return 0;
    }
}
class Circle extends GeometricObject{
    public String name;
    public double radius;
    public double S;
    public Circle(double radius) {
        name="Circle";
        this.radius = radius;
    }
    @Override
    double getArea() {
        return S = 3.14 * radius * radius;
    }
}
class Rectangular extends GeometricObject{
    public String name;
    public double l,w;
    public double S;
    public Rectangular(double l,double w) {
        name="Rectangular";
        this.l=l;
        this.w=w;
    }
    @Override
    double getArea() {
        return S = l*w;
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner in=new Scanner(System.in);
        double r,l,w;
        System.out.println("请输入圆的半径：");
        r=in.nextDouble();
        System.out.println("请输入矩形的长和宽：");
        l=in.nextDouble();
        w=in.nextDouble();
        GeometricObject c=new Circle(r);
        GeometricObject re=new Rectangular(l,w);
        if(c.compareTo(re)==1)System.out.println("圆的面积大");
        else if(c.compareTo(re)==-1)System.out.println("矩形的面积大");
        else System.out.println("面积一样大");
    }
}