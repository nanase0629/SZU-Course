abstract class Animal{
    abstract void moving();
    abstract void eating();
    abstract void yelling();
}

class Tiger extends Animal{
    String name="Tiger";
    @Override
    void moving() {
        System.out.println(name+":爬");
    }
    @Override
    void  eating(){
        System.out.println(name+"：吃肉");
    }
    @Override
    void yelling(){
        System.out.println(name+":吼");
    }
}
class Parrot extends Animal {
    String name = "Parrot";

    @Override
    void moving() {
        System.out.println(name + ":飞");
    }

    @Override
    void eating() {
        System.out.println(name + "：吃虫");
    }

    @Override
    void yelling() {
        System.out.println(name + ":吱");
    }
}
class Dolphin extends Animal{
    String name="Dolphin";
    @Override
    void moving(){
        System.out.println(name+":游");
    }
    @Override
    void eating(){
        System.out.println(name+"：吃鱼");
    }
    @Override
    void yelling(){
        System.out.println(name+":嘤");
    }
}


public class Main {
    public static void main(String[] args) {
        Animal t= new Tiger();
        t.moving();
        t.eating();
        t.yelling();
        System.out.println();
        Animal p=new Parrot();
        p.moving();
        p.eating();
        p.yelling();
        System.out.println();
        Animal d= new Dolphin();
        d.moving();
        d.eating();
        d.yelling();
    }
}