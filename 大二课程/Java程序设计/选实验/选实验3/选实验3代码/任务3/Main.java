import java.util.Scanner;
interface Computable<T>{
    T add(T a);
    T minus(T m);
    T elementwisePrduct(T e);
}
class Vector implements Computable<Vector>{
    int a,b,c,d,e;
    Vector(){
        a=0;
        b=0;
        c=0;
        d=0;
        e=0;
    }
    Vector(int a,int b,int c,int d,int e){
        this.a=a;
        this.b=b;
        this.c=c;
        this.d=d;
        this.e=e;
    }
    public Vector add(Vector v){
        Vector tmp=new Vector();
        tmp.a=a+v.a;
        tmp.b=b+v.b;
        tmp.c=c+v.c;
        tmp.d=d+v.d;
        tmp.e=e+v.e;
        return tmp;
    }
    public Vector minus(Vector v){
        Vector tmp=new Vector();
        tmp.a=a-v.a;
        tmp.b=b-v.b;
        tmp.c=c-v.c;
        tmp.d=d-v.d;
        tmp.e=e-v.e;
        return tmp;
    }
    public Vector elementwisePrduct(Vector v){
        Vector tmp=new Vector();
        tmp.a=a*v.a;
        tmp.b=b*v.b;
        tmp.c=c*v.c;
        tmp.d=d*v.d;
        tmp.e=e*v.e;
        return tmp;
    }
    void show(){
        System.out.println("("+a+","+b+","+c+","+d+","+e+")");
    }
}


public class Main {
    public static void main(String[] args) {
       Scanner in= new Scanner(System.in);
        int a,b,c,d,e;
        System.out.println("请输入向量A的五维：");
        a=in.nextInt();
        b=in.nextInt();
        c=in.nextInt();
        d=in.nextInt();
        e=in.nextInt();
        Vector v1=new Vector(a,b,c,d,e);
        System.out.println("请输入向量B的五维：");
        a=in.nextInt();
        b=in.nextInt();
        c=in.nextInt();
        d=in.nextInt();
        e=in.nextInt();
        Vector v2=new Vector(a,b,c,d,e);
        Vector tmp=new Vector();
        tmp=v1.add(v2);
        System.out.println("A+B的结果为：");
        tmp.show();
        tmp=v1.minus(v2);
        System.out.println("A-B的结果为：");
        tmp.show();
        tmp=v1.elementwisePrduct(v2);
        System.out.println("A*B的结果为：");
        tmp.show();
    }
}