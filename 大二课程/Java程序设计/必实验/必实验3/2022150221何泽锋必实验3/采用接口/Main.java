interface Human{
    abstract void sayHello();
}
class Chinese implements Human{
    String name="Chinese";
    @Override
    public void sayHello() {
        System.out.println(name+":你好我是中文");
    }
}
class French implements Human{
    String name="French";
    @Override
    public void sayHello() {
        System.out.println(name+":你好我是法语");
    }
}
class Japanese implements Human{
    String name="Japanese";
    @Override
    public void sayHello() {
        System.out.println(name+":你好我是日语");
    }
}
class HumanTest{
    Chinese c=new Chinese();
    French f=new French();
    Japanese j=new Japanese();
    public void show(){
        c.sayHello();
        f.sayHello();
        j.sayHello();
    }
}

public class Main {
    public static void main(String[] args) {
        HumanTest ht=new HumanTest();
        ht.show();
    }
}