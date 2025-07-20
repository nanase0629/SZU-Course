package test2;
import Pack.DefaultClass;
public class Main {
    public static void main(String[] args) {
        DefaultClass dc= new DefaultClass();
        System.out.println(dc.bag1_public);
        System.out.println(dc.bag1_protecd);
        System.out.println(dc.bag1_private);
        System.out.println(dc.bag1_default);
    }
}
